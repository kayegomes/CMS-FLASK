// Global variables
let currentUser = null;
let currentEvalType = 'autoavaliacao';
let subordinados = [];

// Initialize application
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM carregado, inicializando aplicação...');
    
    // Load current user
    await loadCurrentUser();
    
    // Setup slider event listeners
    setupSliders();
    
    // Setup form submission
    setupFormSubmission();
    
    // Load initial data
    await loadSubordinados();
    
    console.log('Aplicação inicializada com sucesso');
});

// Load current user
async function loadCurrentUser() {
    console.log('Carregando usuário atual...');
    try {
        const response = await fetch('/api/current_user');
        console.log('Resposta da API /api/current_user:', response.status);
        
        if (response.ok) {
            currentUser = await response.json();
            console.log('Usuário carregado:', currentUser);
            updateUserInterface();
        } else {
            console.error('Erro ao carregar usuário:', response.status);
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        window.location.href = '/login';
    }
}

// Update user interface
function updateUserInterface() {
    if (!currentUser) return;
    
    console.log('Atualizando interface do usuário...');
    
    // Update user info in header
    const userNameElement = document.getElementById('userName');
    const userCargoElement = document.getElementById('userCargo');
    const userAvatarElement = document.getElementById('userAvatar');
    
    if (userNameElement) userNameElement.textContent = currentUser.nome;
    if (userCargoElement) {
        if (currentUser.tipo === 'gestor') {
            userCargoElement.textContent = 'GESTOR';
        } else {
            userCargoElement.textContent = currentUser.cargo || '';
        }
    }
    
    // Update avatar
    if (userAvatarElement) {
        const initials = currentUser.nome.split(' ').map(n => n[0]).join('').substring(0, 2);
        userAvatarElement.textContent = initials;
    }

    // Show/hide evaluation type selector based on user type
    const evalTypeSelector = document.getElementById('evalTypeSelector');
    const autoavaliacaoBtn = document.getElementById('autoavaliacaoBtn');
    
    if (currentUser.tipo === 'funcionario') {
        if (evalTypeSelector) evalTypeSelector.style.display = 'none';
        selectEvalType('autoavaliacao');
    } else {
        if (evalTypeSelector) evalTypeSelector.style.display = 'block';
        // Gestores podem fazer autoavaliação e avaliar subordinados
        selectEvalType('autoavaliacao'); // Começar com autoavaliação por padrão
    }
    
    // Esconder tela de carregamento
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
    }
    
    console.log('Interface do usuário atualizada');
}

// Load subordinados
async function loadSubordinados() {
    console.log('Carregando subordinados...');
    try {
        const response = await fetch('/api/subordinados');
        console.log('Resposta da API /api/subordinados:', response.status);
        if (response.ok) {
            subordinados = await response.json();
            console.log('Subordinados carregados:', subordinados);
            updateAvaliadoSelect();
        } else {
            console.error('Erro ao carregar subordinados:', response.status);
        }
    } catch (error) {
        console.error('Erro ao carregar subordinados:', error);
    }
}

// Update avaliado select
function updateAvaliadoSelect() {
    const select = document.getElementById('nomeAvaliado');
    if (!select) return;
    
    select.innerHTML = '<option value="">Selecione...</option>';

    if (currentEvalType === 'autoavaliacao') {
        // For self-evaluation, only show current user
        if (currentUser) {
            const option = document.createElement('option');
            option.value = currentUser.id;
            option.textContent = currentUser.nome;
            option.selected = true;
            select.appendChild(option);
            select.disabled = true;
        }
    } else {
        // For subordinate evaluation, show subordinates
        select.disabled = false;
        subordinados.forEach(subordinado => {
            if (subordinado.id !== currentUser.id) {
                const option = document.createElement('option');
                option.value = subordinado.id;
                option.textContent = subordinado.nome;
                select.appendChild(option);
            }
        });
    }
}

// Select evaluation type
function selectEvalType(type) {
    currentEvalType = type;
    
    // Update buttons
    document.querySelectorAll('.eval-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`.eval-type-btn.${type}`);
    if (activeBtn) activeBtn.classList.add('active');
    
    updateAvaliadoSelect();
}

// Show tab
function showTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Find the clicked tab button
    const clickedBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => 
        btn.getAttribute('onclick') === `showTab('${tabName}')`
    );
    if (clickedBtn) clickedBtn.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const targetTab = document.getElementById(tabName);
    if (targetTab) targetTab.classList.add('active');

    // Load content based on tab
    switch(tabName) {
        case 'minhas-avaliacoes':
            loadAvaliacoes();
            break;
        case 'colaboradores':
            loadColaboradores();
            break;
        case 'estatisticas':
            loadEstatisticas();
            break;
    }
}

// Setup sliders
function setupSliders() {
    const sliders = document.querySelectorAll('.slider');
    sliders.forEach(slider => {
        // Set initial value display
        updateSliderValue(slider.id);
        
        // Add event listener
        slider.addEventListener('input', function() {
            updateSliderValue(this.id);
        });
    });
}

// Update slider value display
function updateSliderValue(sliderId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(sliderId + '-value');
    
    if (slider && valueDisplay) {
        valueDisplay.textContent = slider.value;
        
        // Update position of value display
        const percentage = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        
    }
}

// Setup form submission
function setupFormSubmission() {
    const form = document.getElementById('avaliacaoForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    console.log('Enviando formulário...');
    
    const formData = new FormData(event.target);
    const data = {};
    
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        if (['producao', 'edicao', 'coordenacao','co_coordenacao', 'pro_atividade', 'criatividade', 
             'resolucao_problemas', 'flexibilidade_adaptabilidade', 'relacionamento_equipe', 
             'relacionamento_outras_areas', 'inteligencia_emocional','lideranca', 'visao_institucional'].includes(key)) {
            data[key] = parseInt(value);
        } else {
            data[key] = value || null;
        }
    }
    
    // Add evaluation type and evaluator info
    data.tipo_avaliacao = currentEvalType;
    data.avaliador_id = currentUser.id;
    
    // Para autoavaliação, o avaliado é o próprio usuário
    if (currentEvalType === 'autoavaliacao') {
        data.avaliado_id = currentUser.id;
    }
    
    console.log('Dados do formulário:', data);
    
    try {
        const response = await fetch('/api/avaliacoes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        console.log('Resposta da API:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Avaliação salva:', result);
            
            showMessage('Avaliação salva com sucesso!', 'success');
            resetForm();
        } else {
            const errorData = await response.json();
            console.error('Erro ao salvar:', errorData);
            showMessage('Erro ao salvar avaliação: ' + (errorData.error || 'Erro desconhecido'), 'error');
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        showMessage('Erro ao salvar avaliação: ' + error.message, 'error');
    }
}

// Reset form
function resetForm() {
    const form = document.getElementById('avaliacaoForm');
    if (form) {
        form.reset();
        
        // Reset sliders to default value
        const sliders = document.querySelectorAll('.slider');
        sliders.forEach(slider => {
            slider.value = 5;
            updateSliderValue(slider.id);
        });
        
        // Reset select
        updateAvaliadoSelect();
    }
}

// Load avaliacoes
async function loadAvaliacoes() {
    const container = document.getElementById('avaliacoesList');
    if (!container) return;
    
    container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Carregando avaliações...</p>';

    try {
        const response = await fetch('/api/avaliacoes');
        if (response.ok) {
            const avaliacoes = await response.json();
            displayAvaliacoes(avaliacoes);
        } else {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar avaliações</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar avaliações:', error);
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar avaliações</p>';
    }
}

// Display avaliacoes
function displayAvaliacoes(avaliacoes) {
    const container = document.getElementById('avaliacoesList');
    if (!container) return;
    
    if (avaliacoes.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Nenhuma avaliação encontrada</p>';
        return;
    }

    container.innerHTML = avaliacoes.map(avaliacao => `
        <div class="avaliacao-card" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin-bottom: 2rem; border: 1px solid var(--glass-border); transition: all 0.3s ease;">
            <div class="avaliacao-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <div>
                    <h3 style="font-size: 1.4rem; font-weight: 600; margin-bottom: 0.5rem;">${avaliacao.avaliado_nome}</h3>
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        <span style="background: ${avaliacao.tipo_avaliacao === 'autoavaliacao' ? 'var(--success-gradient)' : 'var(--accent-gradient)'}; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">${avaliacao.tipo_avaliacao}</span>
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">${new Date(avaliacao.data_avaliacao).toLocaleDateString('pt-BR')}</span>
                    </div>
                </div>
                <div class="media-geral" style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #9c27b0;">${avaliacao.media_geral}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;">Média Geral</div>
                </div>
            </div>
            
            <div class="criterios-detalhes" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Produção</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.producao}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Edição</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.edicao}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Coordenação</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.coordenacao}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Co-coordenação</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.co_coordenacao}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Pró-atividade</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.pro_atividade}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Criatividade</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.criatividade}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Resolução de Problemas</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.resolucao_problemas}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Flexibilidade</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.flexibilidade_adaptabilidade}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Relacionamento Equipe</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.relacionamento_equipe}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Relacionamento Outras Áreas</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.relacionamento_outras_areas}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Inteligência Emocional</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.inteligencia_emocional}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Liderança</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.lideranca}/10</div>
                </div>
                <div class="criterio-item" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Visão Institucional</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #9c27b0;">${avaliacao.visao_institucional}/10</div>
                </div>
            </div>
            
            ${avaliacao.pontos_fortes || avaliacao.pontos_desenvolver ? `
            <div class="pontos-texto" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                ${avaliacao.pontos_fortes ? `
                <div style="background: rgba(76, 175, 80, 0.1); padding: 1.5rem; border-radius: 15px; border-left: 4px solid #4caf50;">
                    <h4 style="color: #4caf50; margin-bottom: 0.75rem; font-size: 1rem; font-weight: 600;">Pontos Fortes</h4>
                    <p style="color: var(--text-secondary); line-height: 1.5;">${avaliacao.pontos_fortes}</p>
                </div>
                ` : ''}
                ${avaliacao.pontos_desenvolver ? `
                <div style="background: rgba(255, 152, 0, 0.1); padding: 1.5rem; border-radius: 15px; border-left: 4px solid #ff9800;">
                    <h4 style="color: #ff9800; margin-bottom: 0.75rem; font-size: 1rem; font-weight: 600;">Pontos a Desenvolver</h4>
                    <p style="color: var(--text-secondary); line-height: 1.5;">${avaliacao.pontos_desenvolver}</p>
                </div>
                ` : ''}
            </div>
            ` : ''}
        </div>
    `).join('');
}

// Load colaboradores
async function loadColaboradores() {
    const container = document.getElementById('colaboradoresList');
    if (!container) return;
    
    container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Carregando colaboradores...</p>';

    try {
        const response = await fetch('/api/usuarios');
        if (response.ok) {
            const usuarios = await response.json();
            displayColaboradores(usuarios);
        } else {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar colaboradores</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar colaboradores:', error);
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar colaboradores</p>';
    }
}

// Display colaboradores
function displayColaboradores(usuarios) {
    const container = document.getElementById('colaboradoresList');
    if (!container) return;
    
    container.innerHTML = usuarios.map(usuario => `
        <div class="criteria-item" style="margin-bottom: 1rem;">
            <h4>${usuario.nome}</h4>
            <p><strong>Email:</strong> ${usuario.email}</p>
            <p><strong>Cargo:</strong> ${usuario.cargo || 'N/A'}</p>
            <p><strong>Tipo:</strong> ${usuario.tipo}</p>
        </div>
    `).join('');
}

// Load estatisticas
async function loadEstatisticas() {
    const container = document.getElementById('estatisticasContent');
    if (!container) return;
    
    container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Carregando estatísticas...</p>';

    try {
        const response = await fetch('/api/avaliacoes/estatisticas');
        if (response.ok) {
            const stats = await response.json();
            displayEstatisticas(stats);
        } else {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar estatísticas</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">Erro ao carregar estatísticas</p>';
    }
}

// Display estatisticas
function displayEstatisticas(stats) {
    const container = document.getElementById('estatisticasContent');
    if (!container) return;
    
    const isGestor = currentUser && currentUser.tipo === 'gestor';
    
    container.innerHTML = `
        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-bottom: 3rem;">
            <div class="stat-card" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; text-align: center; border: 1px solid var(--glass-border);">
                <div style="font-size: 3rem; font-weight: 700; color: #9c27b0; margin-bottom: 0.5rem;">${stats.total_avaliacoes}</div>
                <div style="color: var(--text-secondary); font-size: 1rem; text-transform: uppercase; letter-spacing: 1px;">Total de Avaliações</div>
            </div>
            <div class="stat-card" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; text-align: center; border: 1px solid var(--glass-border);">
                <div style="font-size: 3rem; font-weight: 700; color: #9c27b0; margin-bottom: 0.5rem;">${stats.funcionarios_avaliados}</div>
                <div style="color: var(--text-secondary); font-size: 1rem; text-transform: uppercase; letter-spacing: 1px;">Funcionários Avaliados</div>
            </div>
            <div class="stat-card" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; text-align: center; border: 1px solid var(--glass-border);">
                <div style="font-size: 3rem; font-weight: 700; color: #9c27b0; margin-bottom: 0.5rem;">${stats.media_geral}</div>
                <div style="color: var(--text-secondary); font-size: 1rem; text-transform: uppercase; letter-spacing: 1px;">Média Geral</div>
            </div>
        </div>
        
        ${isGestor && stats.ranking_subordinados && stats.ranking_subordinados.length > 0 ? `
            <div class="ranking-section" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
                <h3 style="margin-bottom: 1.5rem; color: var(--text-primary);">🏆 Ranking dos Subordinados</h3>
                <div class="ranking-list" style="display: flex; flex-direction: column; gap: 1rem;">
                    ${stats.ranking_subordinados.map((item, index) => `
                        <div class="ranking-item" style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 15px; display: flex; align-items: center; gap: 1rem;">
                            <div class="ranking-position" style="background: ${index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : '#9c27b0'}; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2rem;">
                                ${index + 1}
                            </div>
                            <div class="ranking-info" style="flex: 1;">
                                <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">${item.funcionario}</h4>
                                <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">${item.cargo}</p>
                            </div>
                            <div class="ranking-score-auto" style="text-align: right;">
                                <div style="font-size: 2rem; font-weight: 700; color: #ffffffff;">${item.autoavaliacao}</div>
                                <div style="color: var(--text-secondary); font-size: 0.8rem;">AUTOAVALIACAO</div>
                            </div>
                            <div class="ranking-score" style="text-align: right;">
                                <div style="font-size: 2rem; font-weight: 700; color: #9c27b0;">${item.media_geral}</div>
                                <div style="color: var(--text-secondary); font-size: 0.8rem;">MÉDIA GERAL</div>
                            </div>
                        
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        ${stats.comparativo_auto_avaliacao && stats.comparativo_auto_avaliacao.length > 0 ? `
            <div class="comparativo-section" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin-bottom: 2rem; border: 1px solid var(--glass-border);">
                <h3 style="margin-bottom: 1.5rem; color: var(--text-primary);">${isGestor ? 'Comparativo Detalhado' : 'Minha Autoavaliação'}</h3>
                <div class="comparativo-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem;">
                    ${stats.comparativo_auto_avaliacao.map(comp => `
                        <div class="comparativo-item" style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 15px;">
                            <h4 style="margin-bottom: 1.5rem; color: var(--text-primary); font-size: 1.2rem;">${comp.funcionario}</h4>
                            <p style="margin-bottom: 1.5rem; color: var(--text-secondary); font-size: 0.9rem;">${comp.cargo}</p>
                            
                            ${isGestor ? `
                                <div class="medias-resumo" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
                                    <div style="text-align: center; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                                        <div style="font-size: 1.5rem; font-weight: 700; color: #ffffffff;">${comp.autoavaliacao || 'N/A'}</div>
                                        <div style="color: var(--text-secondary); font-size: 0.8rem;">AUTOAVALIAÇÃO</div>
                                    </div>
                                    <div style="text-align: center; padding: 1rem; background: rgba(156, 39, 176, 0.1); border-radius: 10px;">
                                        <div style="font-size: 1.5rem; font-weight: 700; color: #9c27b0;">${comp.avaliacao_gestor || 'N/A'}</div>
                                        <div style="color: var(--text-secondary); font-size: 0.8rem;">AVALIAÇÃO GESTOR</div>
                                    </div>
                                </div>
                                ${comp.diferenca !== null ? `
                                    <div style="text-align: center; margin-bottom: 2rem; padding: 1rem; background: rgba(${comp.diferenca > 0 ? '255, 152, 0' : comp.diferenca < 0 ? '244, 67, 54' : '76, 175, 80'}, 0.1); border-radius: 10px;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: ${comp.diferenca > 0 ? '#ff9800' : comp.diferenca < 0 ? '#f44336' : '#4caf50'};">
                                            ${comp.diferenca > 0 ? '+' : ''}${comp.diferenca}
                                        </div>
                                        <div style="color: var(--text-secondary); font-size: 0.8rem;">DIFERENÇA</div>
                                    </div>
                                ` : ''}
                            ` : `
                                <div style="text-align: center; margin-bottom: 2rem; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                                    <div style="font-size: 2rem; font-weight: 700; color: #4caf50;">${comp.autoavaliacao || 'N/A'}</div>
                                    <div style="color: var(--text-secondary); font-size: 0.8rem;">MINHA MÉDIA GERAL</div>
                                </div>
                            `}
                            
                            ${(isGestor && comp.notas_detalhadas_gestor) || comp.notas_detalhadas_auto ? `
                                <div class="notas-detalhadas">
                                    <h5 style="margin-bottom: 1rem; color: var(--text-primary); font-size: 1rem;"> Notas por Critério</h5>
                                    <div class="criterios-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem;">
                                        ${['producao', 'edicao', 'coordenacao', 'co_coordenacao', 'pro_atividade', 'criatividade', 'resolucao_problemas', 'flexibilidade_adaptabilidade', 'relacionamento_equipe', 'relacionamento_outras_areas', 'inteligencia_emocional', 'lideranca', 'visao_institucional'].map(criterio => {
                                            const nomesCriterios = {
                                                'producao': 'Produção',
                                                'edicao': 'Edição',
                                                'coordenacao': 'Coordenação',
                                                'co_coordenacao': 'Co-coordenação',
                                                'pro_atividade': 'Pró-atividade',
                                                'criatividade': 'Criatividade',
                                                'resolucao_problemas': 'Resolução de Problemas',
                                                'flexibilidade_adaptabilidade': 'Flexibilidade',
                                                'relacionamento_equipe': 'Relacionamento Equipe',
                                                'relacionamento_outras_areas': 'Relacionamento Outras Áreas',
                                                'inteligencia_emocional': 'Inteligência Emocional',
                                                'lideranca': 'Liderança',
                                                'visao_institucional': 'Visão Institucional'
                                            };
                                            
                                            const notaAuto = comp.notas_detalhadas_auto ? comp.notas_detalhadas_auto[criterio] : null;
                                            const notaGestor = isGestor && comp.notas_detalhadas_gestor ? comp.notas_detalhadas_gestor[criterio] : null;
                                            
                                            return `
                                                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                                    <span style="color: var(--text-secondary);">${nomesCriterios[criterio]}:</span>
                                                    <div style="display: flex; gap: 0.5rem;">
                                                        ${notaAuto !== null ? `<span style="color: #ffffffff; font-weight: 600;">${notaAuto}</span>` : ''}
                                                        ${isGestor && notaGestor !== null ? `<span style="color: #9c27b0; font-weight: 600;">${notaGestor}</span>` : ''}
                                                    </div>
                                                </div>
                                            `;
                                        }).join('')}
                                    </div>
                                    
                                    ${comp.notas_detalhadas_auto && comp.notas_detalhadas_auto.pontos_fortes ? `
                                        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                                            <h6 style="margin: 0 0 0.5rem 0; color: #ffffffff; font-size: 0.9rem;"> Pontos Fortes</h6>
                                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.4;">${comp.notas_detalhadas_auto.pontos_fortes}</p>
                                        </div>
                                    ` : ''}
                                    
                                    ${comp.notas_detalhadas_auto && comp.notas_detalhadas_auto.pontos_desenvolver ? `
                                        <div style="margin-top: 1rem; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                                            <h6 style="margin: 0 0 0.5rem 0; color: #ffffffff; font-size: 0.9rem;"> Pontos a Desenvolver</h6>
                                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.4;">${comp.notas_detalhadas_auto.pontos_desenvolver}</p>
                                        </div>
                                    ` : ''}
                                    
                                    ${isGestor && comp.notas_detalhadas_gestor && comp.notas_detalhadas_gestor.pontos_fortes ? `
                                        <div style="margin-top: 1rem; padding: 1rem; background: rgba(156, 39, 176, 0.1); border-radius: 10px;">
                                            <h6 style="margin: 0 0 0.5rem 0; color: #9c27b0; font-size: 0.9rem;"> Pontos Fortes (Gestor)</h6>
                                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.4;">${comp.notas_detalhadas_gestor.pontos_fortes}</p>
                                        </div>
                                    ` : ''}
                                    
                                    ${isGestor && comp.notas_detalhadas_gestor && comp.notas_detalhadas_gestor.pontos_desenvolver ? `
                                        <div style="margin-top: 1rem; padding: 1rem; background: rgba(156, 39, 176, 0.1); border-radius: 10px;">
                                            <h6 style="margin: 0 0 0.5rem 0; color: #9c27b0; font-size: 0.9rem;"> Pontos a Desenvolver (Gestor)</h6>
                                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.4;">${comp.notas_detalhadas_gestor.pontos_desenvolver}</p>
                                        </div>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : `
            <div class="comparativo-section" style="background: var(--glass-bg); backdrop-filter: blur(10px); border-radius: 20px; padding: 2rem; margin-bottom: 2rem; border: 1px solid var(--glass-border); text-align: center;">
                <h3 style="margin-bottom: 1rem; color: var(--text-primary);">${isGestor ? 'Comparativo Detalhado' : 'Minha Autoavaliação'}</h3>
                <p style="color: var(--text-secondary);">Nenhuma avaliação encontrada</p>
            </div>
        `}
    `;
}

// Show message
function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        ${type === 'success' ? 'background: var(--success-gradient);' : 'background: var(--secondary-gradient);'}
    `;
    messageDiv.textContent = message;
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Logout
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
        window.location.href = '/login';
    }
}

