# Requirements Document: Neural Nexus (Epoch 4.0)

## Introduction

O **Neural Nexus** transforma a Aethel de uma fortaleza de verificação formal em um **Organismo de Inteligência Distribuída**. Inspirado pela eficiência da DeepSeek-V3 (Mixture of Experts) e pela filosofia de soberania da Aethel, este sistema implementa:

1. **Destilação Autônoma**: IA que aprende com IAs (GPT-4, Claude, DeepSeek) através de provas matemáticas
2. **Inference Sharding P2P**: Modelos de IA distribuídos em 1000+ nós, custo quase zero
3. **Processamento Verificado**: Cada fragmento de inteligência é vigiado pelo Judge (Z3)
4. **Soberania Computacional**: Empresas pagam para ter IA que aprende com gigantes mas roda 100% offline

**Diferencial Crítico**: Enquanto Petals/BitTorrent apenas distribuem processamento, o Neural Nexus distribui **Processamento Verificado**. Isso impede que a rede P2P seja "envenenada" por dados falsos ou alucinações.

## Glossary

- **Neural_Nexus**: Sistema de inteligência distribuída com verificação formal
- **Destilador_Autônomo**: Motor que compara respostas de múltiplas IAs e destila a "verdade provada"
- **Inference_Sharding**: Técnica de quebrar modelos de IA em fragmentos distribuídos
- **Compute_Royalties**: Taxa cobrada quando um nó processa informação para outro
- **Certificado_de_Destilação**: Prova criptográfica de que uma IA foi "limpa" via verificação formal
- **Local_Engine**: Interface com Ollama para execução local de modelos
- **Teacher_APIs**: GPT-4, Claude, DeepSeek usados como "professores temporários"
- **Verified_Response**: Resposta de IA validada pelo Judge como matematicamente correta
- **LoRA_Training**: Fine-tuning eficiente do modelo local com respostas verificadas
- **Lattice_Shard**: Fragmento de modelo de IA transportado pela rede P2P

## Requirements

### Requirement 1: Local Engine - Interface com Ollama

**User Story:** Como desenvolvedor, quero executar modelos de IA localmente via Ollama, para que eu possa ter inteligência sem depender de APIs externas.

#### Acceptance Criteria

1. WHEN o sistema inicializa, THE Local_Engine SHALL detectar se Ollama está instalado e rodando
2. WHEN Ollama está disponível, THE Local_Engine SHALL listar todos os modelos instalados (DeepSeek-Coder, Llama, etc.)
3. WHEN o usuário solicita uma resposta, THE Local_Engine SHALL enviar o prompt para o modelo Ollama selecionado
4. WHEN Ollama retorna uma resposta, THE Local_Engine SHALL retornar a resposta com metadados (tempo, tokens, modelo)
5. IF Ollama não está disponível, THEN THE Local_Engine SHALL retornar erro claro com instruções de instalação
6. THE Local_Engine SHALL suportar streaming de respostas para UX responsiva
7. THE Local_Engine SHALL medir latência e throughput de cada inferência local

### Requirement 2: Teacher APIs - Ponte com Gigantes

**User Story:** Como arquiteto de sistema, quero consultar GPT-4/Claude/DeepSeek via API, para que eu possa usar suas respostas como "professores" para o modelo local.

#### Acceptance Criteria

1. WHEN o sistema tem chaves de API configuradas, THE Teacher_APIs SHALL suportar GPT-4, Claude, e DeepSeek-V3
2. WHEN o usuário solicita uma resposta, THE Teacher_APIs SHALL enviar o mesmo prompt para todos os professores disponíveis
3. WHEN um professor retorna resposta, THE Teacher_APIs SHALL armazenar a resposta com timestamp e custo
4. THE Teacher_APIs SHALL implementar rate limiting para evitar exceder quotas
5. THE Teacher_APIs SHALL implementar fallback: se GPT-4 falha, tenta Claude, depois DeepSeek
6. THE Teacher_APIs SHALL calcular custo total de cada consulta (tokens × preço por token)
7. WHEN chaves de API não estão configuradas, THE Teacher_APIs SHALL funcionar apenas com Ollama local

### Requirement 3: Destilador Autônomo - Comparação e Verificação

**User Story:** Como usuário, quero que o sistema compare respostas de múltiplas IAs e escolha a melhor via prova matemática, para que eu receba apenas respostas verificadas.

#### Acceptance Criteria

1. WHEN múltiplas IAs retornam respostas, THE Destilador SHALL comparar todas as respostas
2. WHEN respostas contêm código Aethel, THE Destilador SHALL usar o Judge para verificar correção formal
3. WHEN respostas contêm lógica matemática, THE Destilador SHALL usar Z3 para provar equivalência
4. THE Destilador SHALL atribuir score de confiança (0.0-1.0) para cada resposta baseado em:
   - Verificação formal (peso: 0.5)
   - Consistência entre modelos (peso: 0.3)
   - Histórico de acurácia do modelo (peso: 0.2)
5. THE Destilador SHALL selecionar a resposta com maior score de confiança
6. THE Destilador SHALL gerar explicação de por que aquela resposta foi escolhida
7. WHEN nenhuma resposta passa na verificação, THE Destilador SHALL retornar erro com detalhes

### Requirement 4: Cognitive Persistence - Memória de Destilação

**User Story:** Como sistema de aprendizado, quero salvar todas as respostas verificadas, para que o modelo local possa aprender com elas via fine-tuning.

#### Acceptance Criteria

1. WHEN uma resposta é verificada como correta, THE Cognitive_Persistence SHALL salvar:
   - Prompt original
   - Resposta verificada
   - Score de confiança
   - Prova formal (se aplicável)
   - Timestamp e modelo fonte
2. THE Cognitive_Persistence SHALL organizar respostas por categoria (código, matemática, lógica, texto)
3. THE Cognitive_Persistence SHALL implementar deduplicação: respostas idênticas não são salvas duas vezes
4. THE Cognitive_Persistence SHALL manter índice de busca para recuperação rápida
5. WHEN o dataset atinge 1000 exemplos verificados, THE Cognitive_Persistence SHALL notificar que está pronto para fine-tuning
6. THE Cognitive_Persistence SHALL exportar dataset em formato LoRA-compatível (JSON Lines)
7. THE Cognitive_Persistence SHALL implementar compressão para economizar espaço

### Requirement 5: LoRA Training - Fine-Tuning Autônomo

**User Story:** Como modelo local, quero ser treinado com respostas verificadas, para que eu me torne tão inteligente quanto os professores sem precisar de APIs.

#### Acceptance Criteria

1. WHEN o dataset de destilação atinge threshold (1000 exemplos), THE LoRA_Training SHALL iniciar automaticamente
2. THE LoRA_Training SHALL usar apenas respostas com score de confiança > 0.8
3. THE LoRA_Training SHALL treinar o modelo Ollama local usando técnica LoRA (Low-Rank Adaptation)
4. THE LoRA_Training SHALL monitorar loss e accuracy durante treinamento
5. WHEN treinamento completa, THE LoRA_Training SHALL validar o modelo contra conjunto de teste
6. IF accuracy melhora > 5%, THEN THE LoRA_Training SHALL substituir o modelo antigo pelo novo
7. THE LoRA_Training SHALL manter histórico de versões de modelo para rollback

### Requirement 6: Inference Sharding - Distribuição P2P

**User Story:** Como nó da rede, quero hospedar apenas um fragmento do modelo de IA, para que eu possa participar da rede sem hardware potente.

#### Acceptance Criteria

1. WHEN um modelo é carregado, THE Inference_Sharding SHALL quebrar o modelo em N fragmentos (N = número de nós)
2. WHEN um nó se junta à rede, THE Inference_Sharding SHALL atribuir um fragmento único para aquele nó
3. WHEN uma inferência é solicitada, THE Inference_Sharding SHALL:
   - Enviar input para o primeiro nó
   - Cada nó processa seu fragmento e passa para o próximo
   - Último nó retorna output final
4. THE Inference_Sharding SHALL implementar roteamento otimizado (menor latência)
5. THE Inference_Sharding SHALL implementar redundância: cada fragmento existe em 3 nós
6. WHEN um nó falha, THE Inference_Sharding SHALL redirecionar para nó backup
7. THE Inference_Sharding SHALL medir latência end-to-end e otimizar roteamento

### Requirement 7: Verified Inference - Processamento com Prova

**User Story:** Como usuário da rede P2P, quero garantia de que cada fragmento de processamento está correto, para que a rede não seja envenenada por nós maliciosos.

#### Acceptance Criteria

1. WHEN um nó processa um fragmento, THE Verified_Inference SHALL gerar prova criptográfica do processamento
2. THE Verified_Inference SHALL usar Merkle Tree para verificar integridade de cada fragmento
3. WHEN um fragmento é recebido, THE Verified_Inference SHALL verificar a prova antes de aceitar
4. IF prova é inválida, THEN THE Verified_Inference SHALL rejeitar o fragmento e solicitar de nó backup
5. THE Verified_Inference SHALL implementar Byzantine Fault Tolerance (BFT) para tolerar até 33% de nós maliciosos
6. THE Verified_Inference SHALL registrar todas as verificações no Gauntlet Report
7. THE Verified_Inference SHALL implementar slashing: nós que enviam provas inválidas perdem stake

### Requirement 8: Compute Royalties - Modelo de Receita

**User Story:** Como operador de nó, quero ser recompensado quando meu PC processa informação para outros, para que eu tenha incentivo econômico para participar da rede.

#### Acceptance Criteria

1. WHEN um nó processa um fragmento para outro usuário, THE Compute_Royalties SHALL calcular o custo baseado em:
   - Tokens processados
   - Latência do processamento
   - Complexidade do modelo
2. THE Compute_Royalties SHALL cobrar do usuário solicitante em micro-transações
3. THE Compute_Royalties SHALL distribuir 90% para o nó processador, 10% para DIOTEC 360 (Vault de Gênesis)
4. THE Compute_Royalties SHALL implementar sistema de créditos: usuários compram créditos antecipadamente
5. THE Compute_Royalties SHALL implementar desconto por volume: quanto mais você usa, menor o custo por token
6. THE Compute_Royalties SHALL permitir que nós definam seu próprio preço (mercado livre)
7. THE Compute_Royalties SHALL implementar reputação: nós com alta accuracy cobram mais

### Requirement 9: Certificado de Destilação - Prova de Qualidade

**User Story:** Como empresa, quero comprar modelos de IA com certificado de que foram destilados via prova matemática, para que eu tenha garantia de que não alucinam.

#### Acceptance Criteria

1. WHEN um modelo completa destilação, THE Certificado SHALL gerar prova criptográfica contendo:
   - Hash do modelo original
   - Hash do modelo destilado
   - Número de exemplos verificados
   - Score médio de confiança
   - Timestamp e assinatura digital
2. THE Certificado SHALL ser verificável por qualquer terceiro sem acesso ao modelo
3. THE Certificado SHALL incluir relatório de auditoria com estatísticas de verificação
4. THE Certificado SHALL ser registrado na blockchain (Lattice) para imutabilidade
5. THE Certificado SHALL incluir garantia: se o modelo alucinar, DIOTEC 360 reembolsa
6. THE Certificado SHALL ter níveis: Bronze (1k exemplos), Silver (10k), Gold (100k), Platinum (1M)
7. THE Certificado SHALL ser transferível: empresas podem revender modelos certificados

### Requirement 10: Offline Intelligence - SaaS Soberano

**User Story:** Como empresa de inteligência/fábrica, quero uma versão da Aethel que aprende com GPT-4 mas roda 100% offline, para que eu tenha soberania sobre meus dados.

#### Acceptance Criteria

1. THE Offline_Intelligence SHALL incluir:
   - Ollama local pré-configurado
   - Dataset de destilação pré-treinado (10k exemplos)
   - Judge completo para verificação local
   - Interface de administração
2. THE Offline_Intelligence SHALL funcionar sem conexão com internet após instalação
3. THE Offline_Intelligence SHALL permitir que empresa adicione seus próprios dados de treinamento
4. THE Offline_Intelligence SHALL implementar air-gap security: nenhum dado sai da rede local
5. THE Offline_Intelligence SHALL incluir monitoramento de accuracy e drift detection
6. THE Offline_Intelligence SHALL incluir sistema de backup e disaster recovery
7. THE Offline_Intelligence SHALL ter licença enterprise: $50k/ano por instalação

### Requirement 11: Lattice Expansion - Transporte de Fragmentos

**User Story:** Como desenvolvedor de rede, quero adaptar o Lattice P2P para transportar fragmentos de modelos de IA, para que a rede possa escalar para milhões de nós.

#### Acceptance Criteria

1. THE Lattice_Expansion SHALL estender o protocolo P2P para suportar:
   - Fragmentos de modelo (binários grandes, até 1GB)
   - Streaming de inferência (baixa latência)
   - Sincronização de estado de modelo
2. THE Lattice_Expansion SHALL implementar compressão de fragmentos (reduzir tráfego de rede)
3. THE Lattice_Expansion SHALL implementar caching: fragmentos frequentes ficam em cache local
4. THE Lattice_Expansion SHALL implementar discovery: nós anunciam quais fragmentos possuem
5. THE Lattice_Expansion SHALL implementar load balancing: distribuir carga entre nós
6. THE Lattice_Expansion SHALL implementar health checks: detectar nós lentos ou offline
7. THE Lattice_Expansion SHALL implementar metrics: latência, throughput, taxa de erro por nó

### Requirement 12: Sovereign Editor - Interface de Intenção

**User Story:** Como desenvolvedor, quero um editor que não apenas sugere código, mas sugere garantias formais, para que eu escreva código correto por construção.

#### Acceptance Criteria

1. THE Sovereign_Editor SHALL integrar com Neural Nexus para sugestões de código
2. WHEN o usuário digita, THE Sovereign_Editor SHALL mostrar:
   - Sugestão de código (do modelo local)
   - Garantias formais aplicáveis (do Judge)
   - Custo de energia (local vs. P2P)
3. THE Sovereign_Editor SHALL incluir Sentinel Radar mostrando em tempo real:
   - Nós ativos na rede
   - Latência de inferência
   - Custo por token
4. THE Sovereign_Editor SHALL permitir escolher fonte de inteligência:
   - Local (Ollama)
   - P2P (Lattice)
   - Teacher (GPT-4/Claude)
5. THE Sovereign_Editor SHALL incluir painel de destilação mostrando:
   - Exemplos verificados hoje
   - Accuracy do modelo local
   - Próximo treinamento LoRA
6. THE Sovereign_Editor SHALL ser leve (<100MB) e rápido (startup <1s)
7. THE Sovereign_Editor SHALL funcionar offline com modelo local

## Performance Requirements

### Requirement 13: Latência de Destilação

**User Story:** Como usuário, quero que a comparação de respostas seja rápida, para que eu não espere muito tempo.

#### Acceptance Criteria

1. THE Destilador SHALL completar comparação de 3 respostas em <5 segundos
2. THE Destilador SHALL usar paralelização: consultar todos os professores simultaneamente
3. THE Destilador SHALL usar cache: respostas idênticas não são re-verificadas
4. THE Destilador SHALL usar early stopping: se uma resposta tem score 1.0, não verifica outras

### Requirement 14: Throughput de Inference Sharding

**User Story:** Como rede P2P, quero processar milhares de inferências por segundo, para que eu possa competir com APIs centralizadas.

#### Acceptance Criteria

1. THE Inference_Sharding SHALL processar >= 1000 inferências/segundo com 100 nós
2. THE Inference_Sharding SHALL ter latência P95 < 500ms para modelos de 7B parâmetros
3. THE Inference_Sharding SHALL escalar linearmente: 2x nós = 2x throughput
4. THE Inference_Sharding SHALL manter throughput mesmo com 10% de nós offline

### Requirement 15: Custo de Operação

**User Story:** Como operador de rede, quero que o custo por token seja 10x menor que GPT-4, para que eu possa competir no mercado.

#### Acceptance Criteria

1. THE Neural_Nexus SHALL ter custo < $0.001 por 1k tokens (GPT-4 = $0.01)
2. THE Neural_Nexus SHALL ter custo de operação < $100/mês para nó médio
3. THE Neural_Nexus SHALL permitir que usuários "paguem" oferecendo seu próprio PC quando ocioso

## Security Requirements

### Requirement 16: Proteção contra Envenenamento

**User Story:** Como usuário da rede, quero garantia de que nós maliciosos não podem envenenar o modelo, para que eu confie nas respostas.

#### Acceptance Criteria

1. THE Verified_Inference SHALL detectar e rejeitar 100% de fragmentos adulterados
2. THE Verified_Inference SHALL implementar quarentena: nós suspeitos são isolados
3. THE Verified_Inference SHALL implementar auditoria: todas as verificações são registradas
4. THE Verified_Inference SHALL implementar slashing: nós maliciosos perdem stake e são banidos

### Requirement 17: Privacidade de Dados

**User Story:** Como empresa, quero garantia de que meus prompts não vazam para outros nós, para que eu mantenha segredo comercial.

#### Acceptance Criteria

1. THE Neural_Nexus SHALL implementar criptografia end-to-end para todos os prompts
2. THE Neural_Nexus SHALL implementar differential privacy: nós não veem prompts completos
3. THE Neural_Nexus SHALL implementar secure enclaves: processamento em ambiente isolado
4. THE Neural_Nexus SHALL permitir modo privado: inferência 100% local, sem P2P

## Business Model Requirements

### Requirement 18: Plano de Lucro do Império

**User Story:** Como DIOTEC 360, quero múltiplas fontes de receita, para que o império seja sustentável.

#### Acceptance Criteria

1. THE Neural_Nexus SHALL gerar receita via:
   - Compute Royalties (10% de cada transação P2P)
   - SaaS Offline Intelligence ($50k/ano por instalação)
   - Certificados de Destilação ($1k por certificado Gold)
   - Marketplace de modelos certificados (20% de comissão)
2. THE Neural_Nexus SHALL ter meta de receita: $1M/ano no primeiro ano
3. THE Neural_Nexus SHALL ter meta de crescimento: 10x/ano nos primeiros 3 anos
4. THE Neural_Nexus SHALL ter meta de nós: 10k nós ativos no primeiro ano

