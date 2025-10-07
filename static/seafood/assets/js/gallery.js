// Données des images de la galerie
const galleryImages = [
    {
        src: "/static/assets/img/team/team3-image1.png",
        caption: "Flotte de Pêche Moderne - Nos bateaux équipés des dernières technologies pour une pêche efficace et responsable"
    },
    {
        src: "/static/assets/img/team/team3-image2.png",
        caption: "Unité de Transformation - Installation moderne aux normes internationales pour le traitement et la congélation"
    },
    {
        src: "/static/assets/img/team/team3-image3.png",
        caption: "Équipe Professionnelle - Pêcheurs artisanaux expérimentés et techniciens qualifiés au service de la qualité"
    },
    {
        src: "/static/assets/img/team/team3-image1.png",
        caption: "Chambres Froides Modernes - Équipements de stockage de pointe garantissant le respect de la chaîne du froid"
    },
    {
        src: "/static/assets/img/team/team3-image2.png",
        caption: "Port de Nouakchott - Emplacement stratégique pour un accès direct aux meilleures zones de pêche"
    },
    {
        src: "/static/assets/img/team/team3-image3.png",
        caption: "Produits de Qualité Premium - Large gamme de poissons, crustacés et céphalopodes d'une fraîcheur exceptionnelle"
    },
    {
        src: "/static/assets/img/team/team3-image1.png",
        caption: "Contrôle Qualité Rigoureux - Processus de vérification à chaque étape pour garantir la traçabilité et la sécurité"
    },
    {
        src: "/static/assets/img/team/team3-image2.png",
        caption: "Flotte de Livraison - Véhicules réfrigérés pour une livraison dans le respect de la chaîne du froid"
    },
    {
        src: "/static/assets/img/team/team3-image3.png",
        caption: "Certifications Internationales - HACCP et ISO 22000 attestant de notre engagement qualité et sécurité alimentaire"
    }
];

let currentImageIndex = 0;

// Ouvrir le lightbox
function openLightbox(index) {
    currentImageIndex = index;
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const caption = document.getElementById('lightbox-caption');

    img.src = galleryImages[index].src;
    caption.innerHTML = galleryImages[index].caption;
    lightbox.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Empêcher le scroll
}

// Fermer le lightbox
function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
    document.body.style.overflow = 'auto'; // Réactiver le scroll
}

// Changer d'image
function changeImage(direction) {
    currentImageIndex += direction;

    if (currentImageIndex >= galleryImages.length) {
        currentImageIndex = 0;
    } else if (currentImageIndex < 0) {
        currentImageIndex = galleryImages.length - 1;
    }

    const img = document.getElementById('lightbox-img');
    const caption = document.getElementById('lightbox-caption');

    img.style.animation = 'none';
    setTimeout(() => {
        img.src = galleryImages[currentImageIndex].src;
        caption.innerHTML = galleryImages[currentImageIndex].caption;
        img.style.animation = 'zoomIn 0.3s';
    }, 10);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const lightbox = document.getElementById('lightbox');
    const closeBtn = document.querySelector('.lightbox-close');

    if (!lightbox || !closeBtn) return;

    // Fermer avec le bouton X
    closeBtn.onclick = closeLightbox;

    // Fermer en cliquant en dehors de l'image
    lightbox.onclick = function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    };

    // Navigation au clavier
    document.addEventListener('keydown', function(e) {
        if (lightbox.style.display === 'block') {
            if (e.key === 'Escape') {
                closeLightbox();
            } else if (e.key === 'ArrowLeft') {
                changeImage(-1);
            } else if (e.key === 'ArrowRight') {
                changeImage(1);
            }
        }
    });
});
