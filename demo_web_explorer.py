"""
Demo: Web Explorer - Navegação e Extração Web Automatizada
Demonstra as capacidades do Web Explorer com Playwright
"""

from diotec360.core.web_explorer import get_web_explorer
import json


def demo_basic_navigation():
    """Demo 1: Navegação básica"""
    print("\n" + "="*70)
    print("DEMO 1: Navegação Básica")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        # Navegar para uma página
        result = explorer.navigate("https://example.com")
        
        print(f"\n✅ Navegação completa:")
        print(f"   URL: {result['url']}")
        print(f"   Título: {result['title']}")
        print(f"   Status: {result['status']}")
        print(f"   Tempo de carregamento: {result['load_time']:.2f}s")
        
        # Extrair texto
        text = explorer.extract_text()
        print(f"\n📄 Texto extraído ({len(text)} caracteres):")
        print(f"   {text[:200]}...")


def demo_data_extraction():
    """Demo 2: Extração de dados estruturados"""
    print("\n" + "="*70)
    print("DEMO 2: Extração de Dados Estruturados")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        # Navegar para página de exemplo
        explorer.navigate("https://example.com")
        
        # Extrair dados usando seletores
        data = explorer.extract_data({
            "title": "h1",
            "paragraph": "p",
            "link": "a"
        })
        
        print(f"\n📊 Dados extraídos:")
        for field, value in data.items():
            print(f"   {field}: {value}")


def demo_javascript_execution():
    """Demo 3: Execução de JavaScript"""
    print("\n" + "="*70)
    print("DEMO 3: Execução de JavaScript")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        explorer.navigate("https://example.com")
        
        # Executar JavaScript para obter informações da página
        page_info = explorer.execute_script("""
            return {
                url: window.location.href,
                title: document.title,
                links: document.querySelectorAll('a').length,
                images: document.querySelectorAll('img').length,
                paragraphs: document.querySelectorAll('p').length
            }
        """)
        
        print(f"\n🔧 Informações via JavaScript:")
        print(json.dumps(page_info, indent=2))


def demo_screenshot():
    """Demo 4: Captura de screenshot"""
    print("\n" + "="*70)
    print("DEMO 4: Captura de Screenshot")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        explorer.navigate("https://example.com")
        
        # Capturar screenshot
        success = explorer.screenshot("example_screenshot.png", full_page=True)
        
        if success:
            print(f"\n📸 Screenshot salvo: example_screenshot.png")
        else:
            print(f"\n❌ Falha ao capturar screenshot")


def demo_form_interaction():
    """Demo 5: Interação com formulários"""
    print("\n" + "="*70)
    print("DEMO 5: Interação com Formulários (Simulado)")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        # Navegar para página com formulário
        explorer.navigate("https://example.com")
        
        print(f"\n🖱️  Demonstração de interação:")
        print(f"   - Preencher campos: explorer.fill('#email', 'user@example.com')")
        print(f"   - Clicar botões: explorer.click('#submit')")
        print(f"   - Aguardar elementos: explorer.wait_for_selector('#result')")


def demo_cookies():
    """Demo 6: Gerenciamento de cookies"""
    print("\n" + "="*70)
    print("DEMO 6: Gerenciamento de Cookies")
    print("="*70)
    
    with get_web_explorer(headless=True) as explorer:
        explorer.navigate("https://example.com")
        
        # Obter cookies
        cookies = explorer.get_cookies()
        
        print(f"\n🍪 Cookies encontrados: {len(cookies)}")
        for cookie in cookies:
            print(f"   - {cookie.get('name')}: {cookie.get('value')[:50]}...")


def run_all_demos():
    """Executa todos os demos"""
    print("\n" + "="*70)
    print("🌐 WEB EXPLORER - DEMONSTRAÇÃO COMPLETA")
    print("="*70)
    
    try:
        demo_basic_navigation()
        demo_data_extraction()
        demo_javascript_execution()
        demo_screenshot()
        demo_form_interaction()
        demo_cookies()
        
        print("\n" + "="*70)
        print("✅ TODOS OS DEMOS EXECUTADOS COM SUCESSO")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
