const video = document.querySelector(".bg-video");

if (video) {
    const tryPlay = () => {
        const p = video.play();
        if (p && typeof p.catch === "function") {
            p.catch(() => {});
        }
    };

    video.addEventListener("canplay", tryPlay);
    document.addEventListener("click", tryPlay, { once: true });
    tryPlay();
}
