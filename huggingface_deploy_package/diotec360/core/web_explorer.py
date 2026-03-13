"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Web Explorer - Navegação e Extração Web Automatizada
Usa Playwright para interagir com páginas web de forma programática
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Optional, Dict, Any, List
import time
import json


class WebExplorer:
    """
    Web Explorer - Navegador automatizado para extração de dados
    
    Funcionalidades:
    - Navegação em páginas web
    - Extração de conteúdo (texto, HTML, dados estruturados)
    - Interação com elementos (cliques, preenchimento de formulários)
    - Screenshots e PDFs
    - Execução de JavaScript customizado
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Inicializa o Web Explorer
        
        Args:
            headless: Se True, executa navegador sem interface gráfica
            timeout: Timeout padrão em milissegundos (30s)
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def start(self):
        """Inicia o navegador"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        
    def stop(self):
        """Para o navegador e libera recursos"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navega para uma URL
        
        Args:
            url: URL de destino
            
        Returns:
            Dict com informações da navegação
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado. Chame start() primeiro.")
            
        start_time = time.time()
        response = self.page.goto(url, wait_until="domcontentloaded")
        load_time = time.time() - start_time
        
        return {
            "url": url,
            "final_url": self.page.url,
            "title": self.page.title(),
            "status": response.status if response else None,
            "load_time": load_time,
            "success": response.ok if response else False
        }
        
    def extract_text(self, selector: Optional[str] = None) -> str:
        """
        Extrai texto da página
        
        Args:
            selector: Seletor CSS (opcional). Se None, extrai todo o texto
            
        Returns:
            Texto extraído
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        if selector:
            element = self.page.query_selector(selector)
            return element.inner_text() if element else ""
        else:
            return self.page.inner_text("body")
            
    def extract_html(self, selector: Optional[str] = None) -> str:
        """
        Extrai HTML da página
        
        Args:
            selector: Seletor CSS (opcional). Se None, extrai todo o HTML
            
        Returns:
            HTML extraído
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        if selector:
            element = self.page.query_selector(selector)
            return element.inner_html() if element else ""
        else:
            return self.page.content()
            
    def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extrai dados estruturados usando múltiplos seletores
        
        Args:
            selectors: Dict mapeando nomes de campos para seletores CSS
            
        Returns:
            Dict com dados extraídos
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        data = {}
        for field_name, selector in selectors.items():
            try:
                element = self.page.query_selector(selector)
                data[field_name] = element.inner_text() if element else None
            except Exception as e:
                data[field_name] = None
                
        return data
        
    def click(self, selector: str) -> bool:
        """
        Clica em um elemento
        
        Args:
            selector: Seletor CSS do elemento
            
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        try:
            self.page.click(selector)
            return True
        except Exception:
            return False
            
    def fill(self, selector: str, value: str) -> bool:
        """
        Preenche um campo de formulário
        
        Args:
            selector: Seletor CSS do campo
            value: Valor a preencher
            
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        try:
            self.page.fill(selector, value)
            return True
        except Exception:
            return False
            
    def execute_script(self, script: str) -> Any:
        """
        Executa JavaScript na página
        
        Args:
            script: Código JavaScript
            
        Returns:
            Resultado da execução
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        return self.page.evaluate(script)
        
    def screenshot(self, path: str, full_page: bool = False) -> bool:
        """
        Captura screenshot da página
        
        Args:
            path: Caminho para salvar a imagem
            full_page: Se True, captura página inteira (com scroll)
            
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        try:
            self.page.screenshot(path=path, full_page=full_page)
            return True
        except Exception:
            return False
            
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Aguarda até que um elemento apareça na página
        
        Args:
            selector: Seletor CSS do elemento
            timeout: Timeout em milissegundos (usa padrão se None)
            
        Returns:
            True se elemento apareceu, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout or self.timeout)
            return True
        except Exception:
            return False
            
    def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Obtém cookies da sessão atual
        
        Returns:
            Lista de cookies
        """
        if not self.context:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        return self.context.cookies()
        
    def set_cookies(self, cookies: List[Dict[str, Any]]):
        """
        Define cookies para a sessão
        
        Args:
            cookies: Lista de cookies
        """
        if not self.context:
            raise RuntimeError("Web Explorer não foi iniciado.")
            
        self.context.add_cookies(cookies)
        
    def __enter__(self):
        """Context manager: inicia automaticamente"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: para automaticamente"""
        self.stop()


def get_web_explorer(headless: bool = True, timeout: int = 30000) -> WebExplorer:
    """
    Factory function para criar Web Explorer
    
    Args:
        headless: Se True, executa navegador sem interface gráfica
        timeout: Timeout padrão em milissegundos
        
    Returns:
        Instância de WebExplorer
    """
    return WebExplorer(headless=headless, timeout=timeout)
