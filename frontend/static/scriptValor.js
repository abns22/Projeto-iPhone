document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado. Script dashboard.js iniciado.");

    const dashboardLayout = document.querySelector('.dashboard-layout'); 
    const hamburgerBtn = document.getElementById('hamburgerBtn');

    console.log("Elemento Dashboard Layout:", dashboardLayout);
    console.log("Elemento Hamburger Button:", hamburgerBtn);

    if (hamburgerBtn && dashboardLayout) {
        console.log("Botão Hamburger e Dashboard Layout encontrados. Adicionando event listener.");
        hamburgerBtn.addEventListener('click', function() {
            console.log("Botão Hamburger clicado!");
            dashboardLayout.classList.toggle('sidebar-ativa'); 
            console.log("Classe 'sidebar-ativa' alternada no dashboard-layout. Classes atuais:", dashboardLayout.className);
        });
    } else {
        console.error("Erro: Botão Hamburger ou Dashboard Layout não encontrados no DOM.");
    }
});