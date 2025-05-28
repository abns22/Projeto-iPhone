const seletor = document.querySelector('.modelo-escolha');
const formulario = document.querySelector('.formulario');
const perguntas = document.querySelector('.perguntas');

seletor.addEventListener('change', () => {
    if(seletor.value == ''){
        formulario.classList.remove('no-canto')
    } else {
        formulario.classList.add('no-canto');
    }

    if(seletor.value == ''){
        perguntas.classList.add('invisivel');
    } else {
        perguntas.classList.remove('invisivel');
    }

});

const precosBase = {
    "iPhone 11": 1300,
    "iPhone 11 Pro": 1600,
    "iPhone 11 Pro Max": 1900,
    "iPhone 12": 1500,
    "iPhone 12 Mini": 1400,
    "iPhone 12 Pro": 1900,
    "iPhone 12 Pro Max": 2300,
    "iPhone 13": 1800,
    "iPhone 13 Pro": 2500,
    "iPhone 13 Pro Max": 2900,
    "iPhone 13 Mini": 1500,
    "iPhone 14": 2200,
    "iPhone 14 Plus": 2000,
    "iPhone 14 Pro": 2500,
    "iPhone 14 Pro Max": 3000,
    "iPhone 15": 2500,
    "iPhone 15 Plus": 2300,
    "iPhone 15 Pro": 3000,
    "iPhone 15 Pro Max": 3500,
    "iPhone 16e": 2500,
    "iPhone 16 Plus": 2500,
    "iPhone 16": 2800,
    "iPhone 16 Pro": 3400,
    "iPhone 16 Pro Max": 4000,
}

const penalidades = {
  "iPhone 11": {
    tela: 100,
    telaRuim: 150,
    bateria: 50,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 200,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 11 Pro": {
    tela: 150,
    telaRuim: 200,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 250,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 11 Pro Max": {
    tela: 150,
    telaRuim: 250,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 250,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 12": {
    tela: 150,
    telaRuim: 250,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 250,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 12 Pro": {
    tela: 150,
    telaRuim: 250,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 12 Pro Max": {
    tela: 250,
    telaRuim: 250,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 13 Mini": {
    tela: 200,
    telaRuim: 250,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 200,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 13": {
    tela: 300,
    telaRuim: 350,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 250,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 13 Pro": {
    tela: 500,
    telaRuim: 800,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 400,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 13 Pro Max": {
    tela: 500,
    telaRuim: 1000,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 400,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 14 Plus": {
    tela: 300,
    telaRuim: 400,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 14": {
    tela: 300,
    telaRuim: 400,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 14 Pro": {
    tela: 600,
    telaRuim: 1000,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 500,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 14 Pro Max": {
    tela: 600,
    telaRuim: 1000,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 500,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
  "iPhone 15 Plus": {
    tela: 350,
    telaRuim: 500,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 15": {
    tela: 350,
    telaRuim: 500,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 300,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 15 Pro": {
    tela: 600,
    telaRuim: 1200,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 600,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 15 Pro Max": {
    tela: 600,
    telaRuim: 1400,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 600,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 16e": {
    tela: 500,
    telaRuim: 1000,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 350,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 16 Plus": {
    tela: 500,
    telaRuim: 1000,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 350,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 16": {
    tela: 400,
    telaRuim: 800,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 350,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 16 Pro": {
    tela: 700,
    telaRuim: 1500,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 700,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
    "iPhone 16 Pro Max": {
    tela: 800,
    telaRuim: 1800,
    bateria: 80,
    faceId: 200,
    tampa: 100,
    cameraTraseira: 700,
    cameraFrontal: 100,
    som: 50,
    carregar: 100
  },
};

const campos = [
  'tela',
  'telaRuim',
  'bateria',
  'faceId',
  'tampa',
  'cameraTraseira',
  'cameraFrontal',
  'som',
  'carregar'
];







