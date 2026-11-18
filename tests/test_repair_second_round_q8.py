import tempfile
import unittest
from pathlib import Path

from quantage.repair_second_round_q8_inference import observe_attention_cache


class AttentionCacheLogParsing(unittest.TestCase):
    def test_reads_runtime_attention_and_quantized_cache_log_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "server.stderr.txt"
            log.write_text(
                "I llama_context: flash_attn            = enabled\n"
                "I llama_kv_cache: size = 459 MiB, K (q8_0): 229 MiB, V (q8_0): 229 MiB\n"
            )

            observed = observe_attention_cache(log)

        self.assertTrue(observed["flash_attention_enabled"])
        self.assertEqual(observed["cache_type_k"], "q8_0")
        self.assertEqual(observed["cache_type_v"], "q8_0")

    def test_rejects_runtime_report_of_disabled_attention(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "server.stderr.txt"
            log.write_text(
                "I llama_context: flash_attn = disabled\n"
                "I llama_kv_cache: K (q8_0): 229 MiB, V (q8_0): 229 MiB\n"
            )

            observed = observe_attention_cache(log)

        self.assertFalse(observed["flash_attention_enabled"])


if __name__ == "__main__":
    unittest.main()
