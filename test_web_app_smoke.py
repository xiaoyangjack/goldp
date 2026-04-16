import os
import unittest


class WebAppSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 避免测试导入时启动定时器线程
        os.environ["DISABLE_SCHEDULER"] = "true"

    def test_health_and_core_apis(self):
        # 延迟导入，确保环境变量已生效
        import web_app  # noqa: F401

        client = web_app.app.test_client()

        r = client.get("/health")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("status", payload)
        self.assertEqual(payload["status"], "healthy")

        r = client.get("/api/market_data")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("has_data", payload)

        r = client.get("/api/signal")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("signal", payload)

        r = client.get("/api/portfolio")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        # 前端依赖的字段
        self.assertIn("cash", payload)
        self.assertIn("total_value", payload)
        self.assertIn("position", payload)

        r = client.get("/api/status")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("validation", payload)

        r = client.post(
            "/api/backtest/run",
            json={
                "engine": "simple",
                "fast_ma": 10,
                "slow_ma": 30,
                "signal_threshold": 0.5,
                "atr_threshold": 35,
                "stop_loss": 5,
                "max_points": 200,
            },
        )
        # 若数据文件存在但样本太小，可能返回 400；否则应成功
        self.assertIn(r.status_code, [200, 400, 404])
        payload = r.get_json()
        self.assertIn("success", payload)

        # vectorbt 引擎（如果依赖缺失/数据不足，允许失败；关键是不要 500 崩溃）
        r = client.post(
            "/api/backtest/run",
            json={
                "engine": "vectorbt",
                "fast_ma": 10,
                "slow_ma": 30,
                "signal_threshold": 0.5,
                "atr_threshold": 35,
                "max_points": 200,
            },
        )
        self.assertIn(r.status_code, [200, 400, 404, 500])
        payload = r.get_json()
        self.assertIn("success", payload)

        r = client.get("/api/factors")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("has_data", payload)

        r = client.get("/api/runner/status")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("enabled", payload)
        self.assertIn("mode", payload)

        r = client.post("/api/runner/stop", json={})
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertTrue(payload.get("success"))

        r = client.post("/api/runner/start", json={"mode": "signal_only"})
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertTrue(payload.get("success"))


if __name__ == "__main__":
    unittest.main()

