import traceback

try:
    from diotec360.core.whatsapp_gate import WhatsAppGate
    print("✅ WhatsAppGate imported successfully")
    print(f"   Class: {WhatsAppGate}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    traceback.print_exc()
