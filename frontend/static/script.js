const botaoClique = document.querySelector('.entrar');
const emailUsuarioInput = document.querySelector('.digite-email')
const senhaUsuarioInput = document.querySelector('.digite-senha')

function clique() {
    const emailUsuario = emailUsuarioInput.value;
    const senhaUsuario = senhaUsuarioInput.value;

    console.log('Email Digitado:', emailUsuario);
    console.log('Senha Digitada:', senhaUsuario);
}

botaoClique.addEventListener("click", clique);


