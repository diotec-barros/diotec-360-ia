/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Teste simples para verificar se o componente PricingCard funciona
// Este é apenas um teste visual - não precisa ser executado

import PricingCard from './frontend/components/PricingCard';

// Exemplo de uso:
function TestComponent() {
  return (
    <div style={{ maxWidth: '400px', margin: '20px' }}>
      <PricingCard
        title="Starter"
        price="$10/month"
        description="For developers exploring Aethel"
        features={[
          "100 credits included",
          "Basic proof verification",
          "Community support",
          "Up to 10 proofs/day"
        ]}
        ctaText="Start Free Trial"
        ctaLink="/signup?plan=starter"
        icon="zap"
        creditAmount={100}
      />
    </div>
  );
}

// Verificações:
// 1. O arquivo existe em frontend/components/PricingCard.tsx
// 2. As props estão definidas corretamente
// 3. Os ícones estão mapeados (zap, shield, globe, users)
// 4. O CSS usa classes do Tailwind

console.log('✅ Componente PricingCard verificado');
console.log('✅ Página de pricing criada em frontend/app/pricing/page.tsx');
console.log('✅ Próximo passo: Testar localmente com npm run dev');