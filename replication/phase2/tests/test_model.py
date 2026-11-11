"""Synthetic Gate C audits; fixtures contain no market observations or old outputs."""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import tempfile
import unittest
from unittest import mock

import numpy as np
import torch
from torch import nn

import model as m


def hand_fixture() -> tuple[list[str], np.ndarray, np.ndarray]:
    sessions = ["A", "B", "B", "C"]
    overnight = np.array([False, True, True, True])
    supported = np.ones((4, 20), dtype=np.bool_)
    supported[0] = False
    supported[1, 10:] = False
    return sessions, overnight, supported


def synthetic_phase(n_sessions: int = 3) -> m.PhaseData:
    sessions = [f"D{i:02d}" for i in range(n_sessions)]
    signed = np.repeat(np.linspace(-0.03, 0.03, 20)[None, :], n_sessions, axis=0)
    supported = np.ones((n_sessions, 20), dtype=np.bool_)
    supported[0] = False
    overnight = np.ones(n_sessions, dtype=np.bool_)
    overnight[0] = False
    auxiliary = np.repeat((signed / 3.0)[..., None], 3, axis=-1)
    auxiliary[~supported] = np.nan
    rng = np.random.default_rng(321)
    x = rng.normal(0, 0.15, (n_sessions, 20, 48, 16)).astype(np.float32)
    clock = rng.normal(0, 0.2, (n_sessions, 10)).astype(np.float32)

    def inputs(indices: m.IndexArray) -> tuple[m.InputArray, m.InputArray]:
        return x[indices], clock[indices]

    return m.PhaseData(sessions, signed, overnight, auxiliary, supported, inputs, 0.02)


class ModelGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        m.configure_runtime()

    def test_runtime_architecture_parameter_groups_and_fresh_state(self) -> None:
        net = m.fresh_model()
        self.assertEqual(sum(p.numel() for p in net.lstm.parameters()), 6400)
        self.assertEqual(sum(p.numel() for p in net.main.parameters()), 43)
        self.assertEqual(sum(p.numel() for p in net.auxiliary.parameters()), 129)
        self.assertEqual(sum(p.numel() for p in net.parameters()), 6572)
        self.assertEqual(list(dict(net.named_parameters())), [
            "lstm.weight_ih_l0", "lstm.weight_hh_l0", "lstm.bias_ih_l0", "lstm.bias_hh_l0",
            "main.weight", "main.bias", "auxiliary.weight", "auxiliary.bias",
        ])
        self.assertTrue(all(p.dtype == torch.float32 and p.device.type == "cpu" for p in net.parameters()))
        self.assertEqual(torch.get_num_threads(), 4)
        self.assertEqual(torch.get_num_interop_threads(), 1)
        self.assertTrue(torch.are_deterministic_algorithms_enabled())
        optimizer = m.make_optimizer(net)
        self.assertEqual(len(optimizer.state), 0)
        self.assertEqual(len(optimizer.param_groups), 2)
        self.assertEqual([id(p) for p in optimizer.param_groups[0]["params"]],
                         [id(p) for p in net.parameters() if p.ndim == 2])
        self.assertEqual([id(p) for p in optimizer.param_groups[1]["params"]],
                         [id(p) for p in net.parameters() if p.ndim != 2])
        self.assertEqual(optimizer.param_groups[0]["weight_decay"], 0.01)
        self.assertEqual(optimizer.param_groups[1]["weight_decay"], 0)
        for group in optimizer.param_groups:
            self.assertEqual(group["lr"], 0.001)
            self.assertEqual(group["betas"], (0.9, 0.999))
            self.assertEqual(group["eps"], 1e-8)
            self.assertFalse(group["amsgrad"])
            self.assertFalse(group["maximize"])
            self.assertIsNone(group["foreach"])
            self.assertFalse(group["capturable"])
            self.assertFalse(group["differentiable"])
            self.assertIsNone(group["fused"])
        self.assertEqual(m.state_digest(net), m.state_digest(m.fresh_model()))

    def test_exact_initialization_against_independent_draw_sequence(self) -> None:
        net = m.fresh_model()
        actual_rng = torch.get_rng_state().clone()
        random_draw = random.random()
        numpy_draw = np.random.random()
        random.seed(42)
        np.random.seed(42)
        self.assertEqual(random_draw, random.random())
        self.assertEqual(numpy_draw, np.random.random())
        torch.manual_seed(42)
        reference: list[torch.Tensor] = []
        for shape in [(128, 16), (128, 32), (128,), (128,)]:
            reference.append(torch.empty(shape).uniform_(-1 / math.sqrt(32), 1 / math.sqrt(32)))
        for shape in [(1, 42), (3, 42)]:
            weight = torch.empty(shape)
            nn.init.kaiming_uniform_(weight, a=math.sqrt(5))
            reference.append(weight)
            reference.append(torch.empty(shape[0]).uniform_(-1 / math.sqrt(42), 1 / math.sqrt(42)))
        for actual, expected in zip(net.parameters(), reference, strict=True):
            self.assertTrue(torch.equal(actual, expected))
        self.assertTrue(torch.equal(torch.get_rng_state(), actual_rng))
        self.assertTrue(bool(torch.count_nonzero(net.lstm.get_parameter("bias_ih_l0"))))
        self.assertTrue(bool(torch.count_nonzero(net.lstm.get_parameter("bias_hh_l0"))))
        # Building the auxiliary head consumes RNG after otherwise identical main initialization.
        torch.manual_seed(42)
        reference_lstm = nn.LSTM(16, 32, batch_first=True)
        reference_main = nn.Linear(42, 1)
        self.assertTrue(torch.equal(reference_lstm.get_parameter("weight_ih_l0"), net.lstm.get_parameter("weight_ih_l0")))
        self.assertTrue(torch.equal(reference_main.weight, net.main.weight))
        self.assertFalse(torch.equal(torch.get_rng_state(), actual_rng))

    def test_zero_recurrence_and_exact_bias_heads(self) -> None:
        net = m.fresh_model().eval()
        with torch.no_grad():
            for parameter in net.parameters():
                parameter.zero_()
            net.main.bias.fill_(-0.75)
            net.auxiliary.bias.copy_(torch.tensor([-1.0, 0.5, 2.0]))
        x = torch.zeros(3, 48, 16)
        clock = torch.ones(3, 10)
        sequence, (hidden, cell) = net.lstm(x)
        self.assertTrue(torch.equal(sequence, torch.zeros_like(sequence)))
        self.assertTrue(torch.equal(hidden, torch.zeros_like(hidden)))
        self.assertTrue(torch.equal(cell, torch.zeros_like(cell)))
        main, auxiliary = net(x, clock)
        self.assertTrue(torch.equal(main, torch.full((3,), -0.75)))
        self.assertTrue(torch.equal(auxiliary, torch.tensor([[-1.0, 0.5, 2.0]]).repeat(3, 1)))

    def test_direct_gate_recurrence_both_biases_and_sample_reset(self) -> None:
        net = m.fresh_model().eval()
        x = torch.from_numpy(np.random.default_rng(70).normal(0, 0.3, (3, 48, 16)).astype(np.float32))
        clock = torch.zeros(3, 10)
        h, c = torch.zeros(3, 32), torch.zeros(3, 32)
        expected_steps: list[torch.Tensor] = []
        recurrent = dict(net.lstm.named_parameters())
        for k in range(48):
            gates = x[:, k] @ recurrent["weight_ih_l0"].T + recurrent["bias_ih_l0"]
            gates = gates + h @ recurrent["weight_hh_l0"].T + recurrent["bias_hh_l0"]
            i, f, g, o = gates.chunk(4, dim=1)
            c = torch.sigmoid(f) * c + torch.sigmoid(i) * torch.tanh(g)
            h = torch.sigmoid(o) * torch.tanh(c)
            expected_steps.append(h)
        actual, (final_h, final_c) = net.lstm(x)
        torch.testing.assert_close(actual, torch.stack(expected_steps, dim=1), atol=1e-6, rtol=1e-5)
        torch.testing.assert_close(final_h[0], h, atol=1e-6, rtol=1e-5)
        torch.testing.assert_close(final_c[0], c, atol=1e-6, rtol=1e-5)
        original = net(x, clock)[0]
        order = torch.tensor([2, 0, 1])
        torch.testing.assert_close(net(x[order], clock[order])[0], original[order], atol=1e-6, rtol=1e-5)
        alone = torch.cat([net(x[k:k + 1], clock[k:k + 1])[0] for k in range(3)])
        torch.testing.assert_close(alone, original, atol=1e-6, rtol=1e-5)

    def test_shared_dropout_inversion_clock_preservation_and_eval_rng(self) -> None:
        net = m.fresh_model()
        phase = synthetic_phase()
        x_array, clock_array = phase.get_inputs(np.arange(3, dtype=np.int64))
        x = torch.from_numpy(x_array).reshape(-1, 48, 16)
        clock = torch.from_numpy(np.repeat(clock_array, 20, axis=0))
        head_inputs: list[torch.Tensor] = []

        def capture(module: nn.Module, args: tuple[torch.Tensor, ...]) -> None:
            del module
            head_inputs.append(args[0].detach().clone())

        handle_main = net.main.register_forward_pre_hook(capture)
        handle_aux = net.auxiliary.register_forward_pre_hook(capture)
        net.train()
        with torch.no_grad():
            hidden = net.lstm(x)[0][:, -1]
            before = torch.get_rng_state().clone()
            net(x, clock)
            after = torch.get_rng_state().clone()
        self.assertFalse(torch.equal(before, after))
        self.assertTrue(torch.equal(head_inputs[0], head_inputs[1]))
        self.assertTrue(torch.equal(head_inputs[0][:, 32:], clock))
        retained = head_inputs[0][:, :32] != 0
        self.assertTrue(bool(retained.any()) and bool((~retained).any()))
        torch.testing.assert_close(head_inputs[0][:, :32][retained], hidden[retained] / 0.9, atol=1e-7, rtol=1e-6)
        handle_main.remove()
        handle_aux.remove()
        net.eval()
        before = torch.get_rng_state().clone()
        first = net(x, clock)[0]
        second = net(x, clock)[0]
        self.assertTrue(torch.equal(first, second))
        self.assertTrue(torch.equal(before, torch.get_rng_state()))
        expected = net.main(torch.cat((hidden, clock), dim=1)).squeeze(-1)
        self.assertTrue(torch.equal(first, expected))

    def test_global_auxiliary_hierarchy_hand_fixture_float64(self) -> None:
        sessions, overnight, supported = hand_fixture()
        weights = m.auxiliary_weights(sessions, overnight, supported)
        self.assertEqual(weights.sessions, 3)
        self.assertEqual(weights.overnight_sessions, 2)
        self.assertAlmostEqual(weights.mass, 7 / 8, delta=1e-12)
        np.testing.assert_allclose(weights.base.sum(axis=1), [0, 1 / 4, 1 / 4, 1 / 2], atol=1e-12, rtol=0)
        np.testing.assert_allclose(weights.values.sum(axis=1), [0, 1 / 7, 2 / 7, 4 / 7], atol=1e-12, rtol=0)
        self.assertEqual(np.count_nonzero(weights.values[~supported]), 0)
        squared = np.array([0, 9, 4, 1], dtype=np.float64)
        full = float(np.dot(weights.values.sum(axis=1), squared))
        self.assertAlmostEqual(full, 3, delta=1e-12)
        self.assertAlmostEqual(0.1 * full, 0.3, delta=1e-12)
        ab = 3 / 2 * float(np.dot(weights.values[:3].sum(axis=1), squared[:3]))
        c = 3 * float(weights.values[3].sum() * squared[3])
        self.assertAlmostEqual(ab, 51 / 14, delta=1e-12)
        self.assertAlmostEqual(c, 12 / 7, delta=1e-12)
        self.assertAlmostEqual(2 / 3 * ab + 1 / 3 * c, full, delta=1e-12)
        self.assertNotAlmostEqual((ab + c) / 2, full, delta=1e-8)
        primary = float(np.dot(m.origin_weights(sessions), [1, 4, 16, 9]))
        self.assertAlmostEqual(primary, 20 / 3, delta=1e-12)
        self.assertAlmostEqual(float(np.dot(m.origin_weights(sessions[:3]), [1, 4, 16])), 5.5, delta=1e-12)
        self.assertAlmostEqual(float(np.dot(m.origin_weights(["A", "B", "B"]), [2, 4, 8])), 4, delta=1e-12)

    def test_float32_losses_masked_gradients_and_no_nan_times_zero(self) -> None:
        sessions, overnight, mask = hand_fixture()
        weights = m.auxiliary_weights(sessions, overnight, mask)
        main = torch.tensor([1.0, 2.0, 4.0, 3.0]).unsqueeze(1).repeat(1, 20).requires_grad_()
        aux = torch.tensor([7.0, 3.0, 2.0, 1.0]).reshape(4, 1, 1).repeat(1, 20, 3).requires_grad_()
        labels = torch.full((4, 20, 3), math.nan)
        labels[torch.from_numpy(mask)] = 0
        losses = m.batch_losses(main, aux, torch.zeros(4, 20), labels, torch.from_numpy(mask),
                                sessions, torch.from_numpy(weights.values), 3, 0.02)
        self.assertAlmostEqual(float(losses.main.detach()), 20 / 3, delta=2e-6)
        self.assertAlmostEqual(float(losses.auxiliary.detach()), 3, delta=1e-6)
        losses.total.backward()
        self.assertIsNotNone(aux.grad)
        assert aux.grad is not None and main.grad is not None
        self.assertTrue(torch.equal(aux.grad[~torch.from_numpy(mask)], torch.zeros_like(aux.grad[~torch.from_numpy(mask)])))
        expected_aux = 0.1 * 2 / 3 * weights.values[..., None] * aux.detach().numpy()
        np.testing.assert_allclose(aux.grad.numpy(), expected_aux, atol=1e-7, rtol=1e-6)
        expected_main = 2 * m.origin_weights(sessions)[:, None] / 20 * main.detach().numpy()
        np.testing.assert_allclose(main.grad.numpy(), expected_main, atol=1e-7, rtol=1e-6)
        # A-only batch has all-NaN labels. No invalid arithmetic is attempted.
        empty_aux = torch.randn(1, 20, 3, requires_grad=True)
        empty = m.batch_losses(torch.zeros(1, 20), empty_aux, torch.zeros(1, 20),
                               torch.full((1, 20, 3), math.nan), torch.zeros(1, 20, dtype=torch.bool),
                               ["A"], torch.zeros(1, 20), 3, 0.02)
        self.assertEqual(float(empty.auxiliary.detach()), 0)
        empty.auxiliary.backward()
        assert empty_aux.grad is not None
        self.assertTrue(torch.equal(empty_aux.grad, torch.zeros_like(empty_aux)))

    def test_s_over_actual_b_auxiliary_batch_scaling(self) -> None:
        sessions, overnight, mask = hand_fixture()
        weights = m.auxiliary_weights(sessions, overnight, mask)
        expected = [51 / 14, 12 / 7]
        actual: list[float] = []
        for index, expected_loss in zip([np.array([0, 1, 2]), np.array([3])], expected, strict=True):
            n = len(index)
            labels = torch.full((n, 20, 3), math.nan)
            labels[torch.from_numpy(mask[index])] = 0
            auxiliary = torch.tensor([7.0, 3.0, 2.0, 1.0])[index].reshape(n, 1, 1).repeat(1, 20, 3)
            losses = m.batch_losses(torch.zeros(n, 20), auxiliary, torch.zeros(n, 20), labels,
                                    torch.from_numpy(mask[index]), np.asarray(sessions)[index].tolist(),
                                    torch.from_numpy(weights.values[index]), 3, 0.02)
            actual.append(float(losses.auxiliary))
            self.assertAlmostEqual(actual[-1], expected_loss, delta=1e-6)
        self.assertAlmostEqual(2 / 3 * actual[0] + 1 / 3 * actual[1], 3, delta=1e-6)

    def test_tiny_finite_difference_main_and_auxiliary_loss(self) -> None:
        sessions, overnight, mask = hand_fixture()
        weights = m.auxiliary_weights(sessions, overnight, mask)
        generator = np.random.default_rng(2)
        main = torch.tensor(generator.normal(size=(4, 20)), dtype=torch.float64, requires_grad=True)
        auxiliary = torch.tensor(generator.normal(size=(4, 20, 3)), dtype=torch.float64, requires_grad=True)
        labels = torch.full((4, 20, 3), math.nan)
        labels[torch.from_numpy(mask)] = 0.01
        signed = torch.zeros(4, 20)

        def objective() -> torch.Tensor:
            return m.batch_losses(main, auxiliary, signed, labels, torch.from_numpy(mask), sessions,
                                  torch.from_numpy(weights.values), 3, 0.02).total

        objective().backward()
        for tensor, index in [(main, (2, 4)), (auxiliary, (1, 4, 2)), (auxiliary, (1, 18, 2))]:
            assert tensor.grad is not None
            derivative = float(tensor.grad[index])
            with torch.no_grad():
                original = float(tensor[index])
                tensor[index] = original + 1e-6
                plus = float(objective())
                tensor[index] = original - 1e-6
                minus = float(objective())
                tensor[index] = original
            self.assertAlmostEqual((plus - minus) / 2e-6, derivative, delta=1e-7)

    def test_scale_left_quantile_and_training_target_rounding_order(self) -> None:
        signed = np.array([[1.0] * 20, [3.0] * 20], dtype=np.float64)
        self.assertEqual(m.fit_scale(signed, ["A", "B"]), 1.0)
        self.assertEqual(m.fit_scale(np.zeros((2, 20)), ["A", "B"]), 1e-8)
        source = torch.tensor([[-0.0131415926535, 0.000000004167892]], dtype=torch.float64)
        expected = torch.log1p(source.float().abs() / 0.0192837465)
        actual = m.transformed_targets(source, 0.0192837465)
        self.assertEqual(actual.dtype, torch.float32)
        self.assertTrue(torch.equal(actual, expected))

    def test_tiny_recurrent_parameter_finite_differences_double_oracle(self) -> None:
        # Higher precision is used solely for the synthetic derivative oracle;
        # fresh models and all production fitting remain float32.
        phase = synthetic_phase()
        net = m.fresh_model().double().eval()
        x_array, clock_array = phase.get_inputs(np.arange(3, dtype=np.int64))
        x = torch.from_numpy(x_array).reshape(-1, 48, 16).double()
        clock = torch.from_numpy(np.repeat(clock_array, 20, axis=0)).double()
        weights = m.auxiliary_weights(phase.sessions, phase.overnight, phase.auxiliary_mask)

        def objective() -> torch.Tensor:
            hidden = net.lstm(x)[0][:, -1]
            representation = torch.cat((hidden, clock), dim=1)
            main = net.main(representation).reshape(3, 20)
            aux = net.auxiliary(representation).reshape(3, 20, 3)
            return m.batch_losses(main, aux, torch.from_numpy(phase.signed_returns),
                                  torch.from_numpy(phase.auxiliary_returns), torch.from_numpy(phase.auxiliary_mask),
                                  phase.sessions, torch.from_numpy(weights.values), 3, phase.scale).total

        objective().backward()
        for parameter, index in [
            (net.lstm.get_parameter("weight_ih_l0"), (70, 3)), (net.lstm.get_parameter("weight_hh_l0"), (70, 3)),
            (net.lstm.get_parameter("bias_ih_l0"), (70,)), (net.lstm.get_parameter("bias_hh_l0"), (70,)),
            (net.main.weight, (0, 3)), (net.auxiliary.weight, (1, 3)),
        ]:
            assert parameter.grad is not None
            derivative = float(parameter.grad[index])
            with torch.no_grad():
                original = float(parameter[index])
                parameter[index] = original + 1e-6
                plus = float(objective())
                parameter[index] = original - 1e-6
                minus = float(objective())
                parameter[index] = original
            self.assertAlmostEqual((plus - minus) / 2e-6, derivative, delta=1e-7)

    def test_session_shuffle_seed_order_no_drop_last(self) -> None:
        sessions = [f"D{d:02d}" for d in range(19) for _ in range(1 + d % 3)]
        expected = np.array(sorted(set(sessions)))
        np.random.default_rng(43).shuffle(expected)
        before = np.random.get_state()
        batches = list(m.session_batches(sessions, 1))
        after = np.random.get_state()
        self.assertEqual(before[0], after[0])
        np.testing.assert_array_equal(before[1], after[1])
        self.assertEqual(before[2:], after[2:])
        self.assertEqual(len(batches), 2)
        self.assertEqual([len(set(np.asarray(sessions)[batch])) for batch in batches], [16, 3])
        np.testing.assert_array_equal(np.sort(np.concatenate(batches)), np.arange(len(sessions)))
        actual_dates: list[str] = []
        for batch in batches:
            for index in batch:
                date = sessions[int(index)]
                if not actual_dates or actual_dates[-1] != date:
                    actual_dates.append(date)
            for date in set(np.asarray(sessions)[batch]):
                np.testing.assert_array_equal(batch[np.asarray(sessions)[batch] == date], np.flatnonzero(np.asarray(sessions) == date))
        self.assertEqual(actual_dates, expected.tolist())
        self.assertFalse(np.array_equal(np.concatenate(batches), np.concatenate(list(m.session_batches(sessions, 2)))))

    def test_adamw_decay_bias_moments_and_explicit_two_step_math(self) -> None:
        net = m.fresh_model()
        optimizer = m.make_optimizer(net)
        with torch.no_grad():
            for p in net.parameters():
                p.fill_(1)
                p.grad = torch.zeros_like(p)
        optimizer.step()
        for p in net.parameters():
            expected = 1 - 0.001 * 0.01 if p.ndim == 2 else 1
            torch.testing.assert_close(p, torch.full_like(p, expected), atol=0, rtol=0)
        # Reset the optimizer; moment state must be empty, not inherited.
        optimizer = m.make_optimizer(net)
        self.assertEqual(len(optimizer.state), 0)
        weight = net.main.weight
        bias = net.main.bias
        with torch.no_grad():
            weight.fill_(0.7)
            bias.fill_(-0.2)
        expected_w, expected_b = float(weight[0, 0].detach()), float(bias[0].detach())
        mw = vw = mb = vb = 0.0
        for step, (gw, gb) in enumerate([(0.4, -0.3), (-0.2, 0.1)], start=1):
            optimizer.zero_grad()
            weight.grad = torch.full_like(weight, gw)
            bias.grad = torch.full_like(bias, gb)
            mw, vw = 0.9 * mw + 0.1 * gw, 0.999 * vw + 0.001 * gw * gw
            mb, vb = 0.9 * mb + 0.1 * gb, 0.999 * vb + 0.001 * gb * gb
            expected_w *= 1 - 0.001 * 0.01
            expected_w -= 0.001 * (mw / (1 - 0.9 ** step)) / (math.sqrt(vw / (1 - 0.999 ** step)) + 1e-8)
            expected_b -= 0.001 * (mb / (1 - 0.9 ** step)) / (math.sqrt(vb / (1 - 0.999 ** step)) + 1e-8)
            optimizer.step()
            self.assertAlmostEqual(float(weight[0, 0].detach()), expected_w, delta=1e-7)
            self.assertAlmostEqual(float(bias[0].detach()), expected_b, delta=1e-7)

    def test_global_clipping_constant_and_nonfinite_rejection(self) -> None:
        net = m.fresh_model()
        for parameter in net.parameters():
            parameter.grad = torch.zeros_like(parameter)
        assert net.main.bias.grad is not None and net.auxiliary.bias.grad is not None
        net.main.bias.grad[0] = 3
        net.auxiliary.bias.grad[0] = 4
        norm = torch.nn.utils.clip_grad_norm_(net.parameters(), 1, error_if_nonfinite=True)
        self.assertEqual(float(norm), 5)
        self.assertAlmostEqual(float(net.main.bias.grad[0]), 3 / (5 + 1e-6), delta=1e-7)
        self.assertAlmostEqual(float(net.auxiliary.bias.grad[0]), 4 / (5 + 1e-6), delta=1e-7)
        net.main.bias.grad[0] = math.nan
        with self.assertRaises(RuntimeError):
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1, error_if_nonfinite=True)

    def test_empty_auxiliary_still_updates_existing_momentum_and_decay(self) -> None:
        net = m.fresh_model()
        optimizer = m.make_optimizer(net)
        for parameter in net.parameters():
            parameter.grad = torch.ones_like(parameter) * 0.2
        optimizer.step()
        before_weight = net.auxiliary.weight.detach().clone()
        before_bias = net.auxiliary.bias.detach().clone()
        optimizer.zero_grad()
        main, auxiliary = net(torch.zeros(20, 48, 16), torch.zeros(20, 10))
        losses = m.batch_losses(main.reshape(1, 20), auxiliary.reshape(1, 20, 3), torch.zeros(1, 20),
                                torch.full((1, 20, 3), math.nan), torch.zeros(1, 20, dtype=torch.bool),
                                ["A"], torch.zeros(1, 20), 3, 0.02)
        losses.total.backward()
        assert net.auxiliary.weight.grad is not None and net.auxiliary.bias.grad is not None
        self.assertTrue(torch.equal(net.auxiliary.weight.grad, torch.zeros_like(net.auxiliary.weight)))
        self.assertTrue(torch.equal(net.auxiliary.bias.grad, torch.zeros_like(net.auxiliary.bias)))
        optimizer.step()
        self.assertFalse(torch.equal(net.auxiliary.weight, before_weight))
        self.assertFalse(torch.equal(net.auxiliary.bias, before_bias))

    def test_inference_invariance_labels_masks_auxiliary_weights_and_rng(self) -> None:
        phase = synthetic_phase()
        net = m.fresh_model()
        initial_rng = torch.get_rng_state().clone()
        first = m.predict(net, phase.get_inputs, len(phase.sessions))
        self.assertTrue(torch.equal(initial_rng, torch.get_rng_state()))
        phase.signed_returns[:] *= -100
        phase.auxiliary_returns[:] = math.nan
        phase.auxiliary_mask[:] = ~phase.auxiliary_mask
        with torch.no_grad():
            net.auxiliary.weight.fill_(123.0)
            net.auxiliary.bias.fill_(-999.0)
        second = m.predict(net, phase.get_inputs, len(phase.sessions))
        np.testing.assert_array_equal(first, second)
        with torch.no_grad():
            net.auxiliary.weight.fill_(math.inf)
        np.testing.assert_array_equal(first, m.predict(net, phase.get_inputs, len(phase.sessions)))
        self.assertTrue(torch.equal(initial_rng, torch.get_rng_state()))
        self.assertFalse(net.training)

    def test_inference_chronological_chunk32_origin_stock_order(self) -> None:
        requested: list[list[int]] = []
        net = m.fresh_model().eval()
        with torch.no_grad():
            net.main.weight.zero_()
            net.main.weight[0, 32] = 1
            net.main.bias.zero_()

        def getter(indices: m.IndexArray) -> tuple[m.InputArray, m.InputArray]:
            requested.append(indices.tolist())
            x = np.zeros((len(indices), 20, 48, 16), dtype=np.float32)
            clock = np.zeros((len(indices), 10), dtype=np.float32)
            clock[:, 0] = indices
            return x, clock

        actual = m.predict(net, getter, 65)
        self.assertEqual([len(part) for part in requested], [32, 32, 1])
        self.assertEqual(sum(requested, []), list(range(65)))
        np.testing.assert_array_equal(actual, np.repeat(np.arange(65, dtype=np.float32)[:, None], 20, axis=1))

    def test_selector_float32_target_and_float64_hierarchy_only(self) -> None:
        phase = synthetic_phase()
        net = m.fresh_model().eval()
        prediction = m.predict(net, phase.get_inputs, 3)
        target = torch.log1p(torch.from_numpy(phase.signed_returns).float().abs() / phase.scale)
        origin_loss = (torch.from_numpy(prediction) - target).square().mean(dim=1).numpy().astype(np.float64)
        expected = float(np.dot(origin_loss, m.origin_weights(phase.sessions)))
        phase.auxiliary_returns[:] = math.nan
        phase.auxiliary_mask[:] = False
        self.assertEqual(m.validation_loss(net, phase), expected)

    def test_selector_qualified_equality_raw_minimum_patience_and_zero(self) -> None:
        selector = m.Selector()
        self.assertTrue(selector.update(2))
        self.assertFalse(selector.update(1.999))
        self.assertEqual((selector.selected, selector.raw_epoch, selector.patience), (1, 2, 1))
        self.assertTrue(selector.update(1.998))
        self.assertEqual((selector.selected, selector.raw_epoch, selector.patience), (3, 3, 0))
        positive = m.Selector()
        for _ in range(12):
            positive.update(1)
        self.assertEqual((positive.epoch, positive.selected, positive.patience, positive.stop_reason), (12, 1, 11, "patience"))
        with self.assertRaises(RuntimeError):
            positive.update(1)
        zero = m.Selector()
        for _ in range(60):
            self.assertTrue(zero.update(0))
        self.assertEqual((zero.selected, zero.patience, zero.stop_reason), (60, 0, "epoch_cap"))
        precedence = m.Selector(epoch=59, selected=50, best=1, raw_best=1, raw_epoch=50, patience=9)
        self.assertFalse(precedence.update(1))
        self.assertEqual(precedence.stop_reason, "patience")
        for bad in [math.nan, math.inf, -0.01]:
            with self.assertRaises(ValueError):
                m.Selector().update(bad)

    def test_selector_clone_is_independent_and_full_state(self) -> None:
        net = m.fresh_model()
        selector = m.Selector()
        selector.update(2, net)
        assert selector.best_state is not None
        self.assertEqual(set(selector.best_state), set(net.state_dict()))
        copied = selector.best_state["auxiliary.bias"].clone()
        with torch.no_grad():
            net.auxiliary.bias.add_(1)
        self.assertTrue(torch.equal(selector.best_state["auxiliary.bias"], copied))

    def test_actual_epoch_two_updates_last_batch_and_rng_progression(self) -> None:
        phase = synthetic_phase(17)
        net = m.fresh_model()
        optimizer = m.make_optimizer(net)
        weights = m.auxiliary_weights(phase.sessions, phase.overnight, phase.auxiliary_mask)
        initial_rng = torch.get_rng_state().clone()
        with mock.patch.object(optimizer, "step", wraps=optimizer.step) as step:
            with mock.patch("torch.nn.utils.clip_grad_norm_", wraps=torch.nn.utils.clip_grad_norm_) as clip:
                record = m.train_epoch(net, optimizer, phase, weights, 1)
                self.assertEqual(step.call_count, 2)
                self.assertEqual(clip.call_count, 2)
        self.assertEqual(record.updates, 2)
        self.assertTrue(math.isfinite(record.batch_main_mean))
        self.assertTrue(math.isfinite(record.batch_aux_three_head_mean))
        self.assertFalse(torch.equal(initial_rng, torch.get_rng_state()))
        for state in optimizer.state.values():
            self.assertEqual(float(state["step"]), 2)
        # A fresh phase restores parameters and empty moments despite prior updates.
        fresh = m.fresh_model()
        self.assertEqual(len(m.make_optimizer(fresh).state), 0)
        self.assertNotEqual(m.state_digest(net), m.state_digest(fresh))

    def test_synthetic_refit_receipts_callbacks_reload_and_no_retry(self) -> None:
        phase = synthetic_phase()
        callback_records: list[m.EpochRecord] = []
        with tempfile.TemporaryDirectory(prefix="s2c-synthetic-refit-") as tmp:
            output = Path(tmp) / "run"
            result = m.train_refit(phase, 2, output_dir=output, progress=callback_records.append)
            self.assertEqual(result.selected_epochs, 2)
            self.assertEqual(len(callback_records), 2)
            self.assertEqual([record.epoch for record in callback_records], [1, 2])
            receipt = json.loads((output / "completed.json").read_text())
            self.assertEqual(receipt["status"], "COMPLETE")
            self.assertEqual(receipt["epochs_executed"], 2)
            started = json.loads((output / "started.json").read_text())
            self.assertEqual(started["initial_optimizer_state_entries"], 0)
            self.assertEqual(started["initial_digest"], result.initial_digest)
            self.assertEqual(len((output / "trace.jsonl").read_text().splitlines()), 2)
            reload = m.load_state(output / "final_state.pt")
            np.testing.assert_array_equal(m.predict(result.model, phase.get_inputs, 3), m.predict(reload, phase.get_inputs, 3))
            self.assertEqual(m.state_digest(reload), result.final_digest)
            with self.assertRaises(FileExistsError):
                m.train_refit(phase, 2, output_dir=output)

    def test_synthetic_selector_discards_raw_minimum_and_fresh_refit(self) -> None:
        phase = synthetic_phase()
        values = [2, 1.999, 1.998] + [1.9979] * 10
        digest_by_epoch: list[str] = []
        with tempfile.TemporaryDirectory(prefix="s2c-synthetic-selector-") as tmp:
            output = Path(tmp) / "select"

            def value(net: m.S2CModel, validation: m.PhaseData) -> float:
                del validation
                digest_by_epoch.append(m.state_digest(net))
                return values[len(digest_by_epoch) - 1]

            with mock.patch.object(m, "validation_loss", side_effect=value):
                result = m.train_selector(phase, phase, output_dir=output)
            self.assertEqual(result.selected_epochs, 3)
            self.assertEqual(len(result.records), 13)
            self.assertEqual(result.final_digest, digest_by_epoch[2])
            self.assertIsNotNone(result.selector)
            assert result.selector is not None
            self.assertEqual(result.selector.raw_epoch, 4)
            selected = m.load_state(output / "selected_state.pt")
            self.assertEqual(m.state_digest(selected), result.final_digest)
            refit = m.train_refit(phase, result.selected_epochs, output_dir=Path(tmp) / "refit")
            self.assertEqual(refit.initial_digest, result.initial_digest)
            self.assertEqual(len(refit.records), 3)
            # Identical synthetic phases + selector eval consumes no RNG: exact trajectories.
            self.assertEqual(refit.final_digest, result.final_digest)

    def test_failure_receipt_no_implicit_second_fit(self) -> None:
        phase = synthetic_phase()
        with tempfile.TemporaryDirectory(prefix="s2c-synthetic-failure-") as tmp:
            output = Path(tmp) / "run"
            with mock.patch.object(m, "train_epoch", side_effect=RuntimeError("synthetic injected failure")) as run:
                with self.assertRaisesRegex(RuntimeError, "synthetic injected failure"):
                    m.train_refit(phase, 2, output_dir=output)
                self.assertEqual(run.call_count, 1)
            failure = json.loads((output / "failure.json").read_text())
            self.assertEqual(failure["status"], "FAILED_STOP_NO_RETRY")
            self.assertFalse((output / "completed.json").exists())
            with self.assertRaises(FileExistsError):
                m.train_refit(phase, 2, output_dir=output)

    def test_invalid_phase_inputs_and_zero_global_mass_block(self) -> None:
        sessions, overnight, mask = hand_fixture()
        with self.assertRaisesRegex(ValueError, "positive"):
            m.auxiliary_weights(sessions, overnight, np.zeros_like(mask))
        mask[0, 0] = True
        with self.assertRaisesRegex(ValueError, "Intraday"):
            m.auxiliary_weights(sessions, overnight, mask)
        net = m.fresh_model()
        with self.assertRaisesRegex(ValueError, "float32"):
            net(torch.zeros(1, 48, 16, dtype=torch.float64), torch.zeros(1, 10))
        x = torch.zeros(1, 48, 16)
        x[0, 0, 0] = math.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            net(x, torch.zeros(1, 10))


if __name__ == "__main__":
    unittest.main(verbosity=2)
