import pytest
import unittest.mock as mock
from barkland.main import generate_unique_dog_names
from barkland.models.dog import DogProfile, DogState, Personality, DogNeeds
from barkland.agents.dog_agent import DogAgent

def test_generate_unique_dog_names_count():
    # Test generating 5 names
    names = generate_unique_dog_names(5)
    assert len(names) == 5
    # Verify uniqueness
    assert len(set(names)) == 5

def test_generate_unique_dog_names_large_count():
    # Test generating 50 names (ensures unique combos or fallback executes)
    names = generate_unique_dog_names(50)
    assert len(names) == 50
    assert len(set(names)) == 50

@pytest.mark.asyncio
async def test_speak_prompt_includes_sleeping_rule():
    # Setup profile in SLEEPING state
    profile = DogProfile(
        name="Sir Barkley", 
        breed="Golden Retriever", 
        personality=Personality.PHILOSOPHER,
        state=DogState.SLEEPING
    )
    agent = DogAgent(profile)
    
    # Mock GenAI client
    with mock.patch('google.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.aio.models.generate_content = mock.AsyncMock()
        mock_instance.aio.models.generate_content.return_value.text = '{"bark": "Zzz", "translation": "Sleeping (Dreaming of bacon)"}'
        
        # Call speak
        response = await agent.speak(ignore_cache=True)
        
        # Verify prompt contained specific SLEEPING instructions
        called_args = mock_instance.aio.models.generate_content.call_args
        prompt_text = called_args.kwargs['contents']
        
        assert "Sir Barkley" in prompt_text
        assert "SLEEPING" in prompt_text
        assert "Dreaming of" in prompt_text or "MUST be a short, funny dream description" in prompt_text

@pytest.mark.asyncio
async def test_speak_prompt_includes_eating_rule():
    profile = DogProfile(
        name="Sir Barkley", 
        breed="Golden Retriever", 
        personality=Personality.FOODIE,
        state=DogState.EATING
    )
    agent = DogAgent(profile)
    
    with mock.patch('google.genai.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.aio.models.generate_content = mock.AsyncMock()
        mock_instance.aio.models.generate_content.return_value.text = '{"bark": "Crunch", "translation": "Yum"}'
        
        await agent.speak(ignore_cache=True)
        
        called_args = mock_instance.aio.models.generate_content.call_args
        prompt_text = called_args.kwargs['contents']
        
        assert "Sir Barkley" in prompt_text
        assert "EATING" in prompt_text

@pytest.mark.asyncio
async def test_speak_proxy_routing_to_sandbox_http_endpoint():
    # Force ENVIRONMENT=prod locally for this mock securely escaping local short-circuits
    with mock.patch.dict("os.environ", {"ENVIRONMENT": "production"}):
        profile = DogProfile(
            name="ProxyPup", 
            breed="Husky", 
            personality=Personality.JOCK,
            state=DogState.PLAYING
        )
        agent = DogAgent(profile)
        
        # Mock a SandboxClient
        mock_sandbox = mock.Mock()
        mock_sandbox.is_ready.return_value = True
        mock_sandbox.base_url = "http://sandbox-router-svc:8080"
        mock_sandbox.sandbox_name = "test-sandbox-dog"
        
        # Mock httpx.AsyncClient.post response
        mock_response = mock.Mock()
        mock_response.json.return_value = {"bark": "Proxy woof!", "translation": "Over the wire!"}
        mock_response.raise_for_status = mock.Mock()
        
        with mock.patch("httpx.AsyncClient") as MockClient:
            # Wire magic methods for async context manager (`async with`)
            mock_client_instance = MockClient.return_value.__aenter__.return_value
            mock_client_instance.post = mock.AsyncMock(return_value=mock_response)
            
            response = await agent.speak(sandbox_client=mock_sandbox, ignore_cache=True)
            
            # Assertions
            mock_client_instance.post.assert_called_once()
            called_url = mock_client_instance.post.call_args[0][0]
            called_headers = mock_client_instance.post.call_args.kwargs.get("headers", {})
            
            assert called_url == "http://sandbox-router-svc:8080/api/dog/speak"
            assert called_headers.get("X-Sandbox-ID") == "test-sandbox-dog"
            assert called_headers.get("X-Sandbox-Port") == "8000"
            
            called_json = mock_client_instance.post.call_args.kwargs["json"]
            assert called_json["name"] == "ProxyPup"
            
            assert response.bark == "Proxy woof!"
            assert response.translation == "Over the wire!"
