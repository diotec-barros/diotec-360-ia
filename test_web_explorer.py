"""
Testes para Web Explorer
"""

import pytest
from diotec360.core.web_explorer import WebExplorer, get_web_explorer
import os


if os.environ.get('DIOTEC360_OFFLINE', '').lower() in {'1', 'true', 'yes', 'on'} or \
    os.environ.get('DIOTEC360_TEST_MODE', '').lower() in {'1', 'true', 'yes', 'on'}:
    pytest.skip("offline mode", allow_module_level=True)


class TestWebExplorerBasics:
    """Testes básicos do Web Explorer"""
    
    def test_initialization(self):
        """Testa inicialização do Web Explorer"""
        explorer = WebExplorer(headless=True, timeout=30000)
        assert explorer.headless is True
        assert explorer.timeout == 30000
        assert explorer.browser is None
        assert explorer.page is None
        
    def test_start_stop(self):
        """Testa iniciar e parar o navegador"""
        explorer = WebExplorer(headless=True)
        explorer.start()
        
        assert explorer.browser is not None
        assert explorer.page is not None
        
        explorer.stop()
        
    def test_context_manager(self):
        """Testa uso como context manager"""
        with get_web_explorer(headless=True) as explorer:
            assert explorer.browser is not None
            assert explorer.page is not None


class TestWebExplorerNavigation:
    """Testes de navegação"""
    
    def test_navigate_success(self):
        """Testa navegação bem-sucedida"""
        with get_web_explorer(headless=True) as explorer:
            result = explorer.navigate("https://example.com")
            
            assert result["success"] is True
            assert result["status"] == 200
            assert "example" in result["title"].lower()
            assert result["load_time"] > 0
            
    def test_navigate_without_start(self):
        """Testa navegação sem iniciar o navegador"""
        explorer = WebExplorer(headless=True)
        
        with pytest.raises(RuntimeError):
            explorer.navigate("https://example.com")


class TestWebExplorerExtraction:
    """Testes de extração de dados"""
    
    def test_extract_text(self):
        """Testa extração de texto"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            text = explorer.extract_text()
            
            assert len(text) > 0
            assert "example" in text.lower()
            
    def test_extract_text_with_selector(self):
        """Testa extração de texto com seletor"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            title = explorer.extract_text("h1")
            
            assert len(title) > 0
            
    def test_extract_html(self):
        """Testa extração de HTML"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            html = explorer.extract_html()
            
            assert len(html) > 0
            assert "<html" in html.lower()
            
    def test_extract_data(self):
        """Testa extração de dados estruturados"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            data = explorer.extract_data({
                "title": "h1",
                "paragraph": "p"
            })
            
            assert "title" in data
            assert "paragraph" in data
            assert data["title"] is not None


class TestWebExplorerInteraction:
    """Testes de interação"""
    
    def test_execute_script(self):
        """Testa execução de JavaScript"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            result = explorer.execute_script("return document.title")
            
            assert result is not None
            assert len(result) > 0
            
    def test_execute_script_complex(self):
        """Testa execução de JavaScript complexo"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            result = explorer.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    links: document.querySelectorAll('a').length
                }
            """)
            
            assert "url" in result
            assert "title" in result
            assert "links" in result


class TestWebExplorerScreenshot:
    """Testes de screenshot"""
    
    def test_screenshot(self):
        """Testa captura de screenshot"""
        screenshot_path = "test_screenshot.png"
        
        # Remove screenshot anterior se existir
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            success = explorer.screenshot(screenshot_path)
            
            assert success is True
            assert os.path.exists(screenshot_path)
            
        # Limpar
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


class TestWebExplorerCookies:
    """Testes de gerenciamento de cookies"""
    
    def test_get_cookies(self):
        """Testa obtenção de cookies"""
        with get_web_explorer(headless=True) as explorer:
            explorer.navigate("https://example.com")
            cookies = explorer.get_cookies()
            
            assert isinstance(cookies, list)


def run_tests():
    """Executa todos os testes"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
