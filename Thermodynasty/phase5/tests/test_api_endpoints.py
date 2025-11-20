"""
Integration Tests for API Endpoints

Tests all REST API endpoints including authentication,
validation, and error handling.
"""

import pytest
import numpy as np


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_liveness_probe(self, client):
        """Test liveness probe endpoint"""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_readiness_probe(self, client):
        """Test readiness probe endpoint"""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert b"http_requests_total" in response.content


@pytest.mark.integration
class TestPredictEndpoint:
    """Test /v1/predict endpoint"""

    def test_predict_success(self, client, predict_request_data, auth_headers):
        """Test successful prediction request"""
        response = client.post(
            "/v1/predict",
            json=predict_request_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "prediction" in data
        assert "regime" in data
        assert "confidence" in data
        assert "approved" in data
        assert "processing_time_ms" in data

        # Validate regime
        assert data["regime"] in ["equilibrium", "transition", "critical"]

        # Validate confidence
        assert 0.0 <= data["confidence"] <= 1.0

        # Validate approved is boolean
        assert isinstance(data["approved"], bool)

    def test_predict_unauthenticated(self, client, predict_request_data):
        """Test prediction without authentication"""
        response = client.post("/v1/predict", json=predict_request_data)

        assert response.status_code == 401

    def test_predict_invalid_energy_map(self, client, auth_headers):
        """Test prediction with invalid energy map"""
        invalid_data = {
            "energy_map": "not_a_list",
            "domain": "plasma",
            "cluster": "cluster_001",
            "node": "node_001"
        }

        response = client.post(
            "/v1/predict",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_predict_missing_fields(self, client, auth_headers):
        """Test prediction with missing required fields"""
        incomplete_data = {
            "energy_map": [[1.0, 2.0], [3.0, 4.0]]
            # Missing domain, cluster, node
        }

        response = client.post(
            "/v1/predict",
            json=incomplete_data,
            headers=auth_headers
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestDiffuseEndpoint:
    """Test /v1/diffuse endpoint"""

    def test_diffuse_success(self, client, diffuse_request_data, auth_headers):
        """Test successful diffusion sampling"""
        response = client.post(
            "/v1/diffuse",
            json=diffuse_request_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "generated_sample" in data
        assert "energy_fidelity" in data
        assert "total_energy" in data
        assert "processing_time_ms" in data

        # Validate sample shape
        sample = np.array(data["generated_sample"])
        expected_shape = tuple(diffuse_request_data["shape"])
        assert sample.shape == expected_shape

        # Validate energy fidelity
        assert 0.0 <= data["energy_fidelity"] <= 1.0

    def test_diffuse_with_custom_parameters(self, client, auth_headers):
        """Test diffusion with custom parameters"""
        custom_data = {
            "shape": [8, 8],
            "num_inference_steps": 5,
            "energy_guidance_scale": 2.0,
            "temperature": 0.5,
            "seed": 123
        }

        response = client.post(
            "/v1/diffuse",
            json=custom_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should succeed with custom params
        assert "generated_sample" in data

    def test_diffuse_invalid_shape(self, client, auth_headers):
        """Test diffusion with invalid shape"""
        invalid_data = {
            "shape": [0, 0],  # Invalid: zero dimensions
            "num_inference_steps": 10
        }

        response = client.post(
            "/v1/diffuse",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_diffuse_rate_limiting(self, client, auth_headers):
        """Test rate limiting on diffuse endpoint"""
        # Make multiple rapid requests
        responses = []
        for _ in range(150):  # Exceed default rate limit of 100
            responses.append(
                client.post(
                    "/v1/diffuse",
                    json={"shape": [4, 4], "num_inference_steps": 1},
                    headers=auth_headers
                )
            )

        # Should eventually hit rate limit
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes  # Too Many Requests


@pytest.mark.integration
class TestProofEndpoint:
    """Test /v1/proof endpoint"""

    def test_proof_valid(self, client, proof_request_data, auth_headers):
        """Test proof validation with valid input"""
        response = client.post(
            "/v1/proof",
            json=proof_request_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "valid" in data
        assert "confidence" in data
        assert "verification_details" in data

        assert isinstance(data["valid"], bool)
        assert 0.0 <= data["confidence"] <= 1.0

    def test_proof_invalid_regime_claim(self, client, auth_headers):
        """Test proof with invalid regime claim"""
        invalid_proof = {
            "energy_map": np.random.randn(16, 16).tolist(),
            "claimed_regime": "invalid_regime",  # Not a valid regime
            "metadata": {}
        }

        response = client.post(
            "/v1/proof",
            json=invalid_proof,
            headers=auth_headers
        )

        # Should either reject or return invalid proof
        assert response.status_code in [200, 422]


@pytest.mark.integration
class TestMarketEndpoint:
    """Test /v1/market/pricing endpoint"""

    def test_get_pricing(self, client, auth_headers):
        """Test market pricing endpoint"""
        response = client.get("/v1/market/pricing", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "ceu_price" in data
        assert "pft_price" in data
        assert "last_updated" in data

        # Validate prices are positive
        assert data["ceu_price"] > 0
        assert data["pft_price"] > 0


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_endpoint(self, client):
        """Test request to non-existent endpoint"""
        response = client.get("/nonexistent/endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test wrong HTTP method"""
        response = client.get("/v1/predict")  # Should be POST

        assert response.status_code == 405

    def test_malformed_json(self, client, auth_headers):
        """Test malformed JSON payload"""
        response = client.post(
            "/v1/predict",
            data="not valid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_oversized_request(self, client, auth_headers):
        """Test oversized request body"""
        # Create very large energy map
        large_map = np.random.randn(1000, 1000).tolist()

        response = client.post(
            "/v1/predict",
            json={
                "energy_map": large_map,
                "domain": "test",
                "cluster": "test",
                "node": "test"
            },
            headers=auth_headers
        )

        # Should handle gracefully (may succeed or reject based on limits)
        assert response.status_code in [200, 413, 422]


@pytest.mark.integration
class TestCORSHeaders:
    """Test CORS headers"""

    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/v1/predict",
            headers={"Origin": "http://example.com"}
        )

        # Should allow CORS
        assert "access-control-allow-origin" in response.headers

    def test_cors_actual_request(self, client, auth_headers):
        """Test CORS headers on actual request"""
        response = client.get(
            "/health/live",
            headers={**auth_headers, "Origin": "http://example.com"}
        )

        assert "access-control-allow-origin" in response.headers


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance and load tests"""

    def test_concurrent_requests(self, client, predict_request_data, auth_headers):
        """Test handling of concurrent requests"""
        import concurrent.futures

        def make_request():
            return client.post(
                "/v1/predict",
                json=predict_request_data,
                headers=auth_headers
            )

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(r.status_code == 200 for r in results)

    def test_response_time(self, client, auth_headers):
        """Test API response time"""
        import time

        start = time.time()
        response = client.get("/health/live", headers=auth_headers)
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.1  # Should respond in < 100ms
