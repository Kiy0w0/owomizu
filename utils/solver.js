// HCaptcha & Cloudflare Auto-Clicker
// Transparent & Safe Script for OwOmizu

(function () {
    console.log("🧩 OwOmizu Solver Started...");

    function clickWhenAvailable(selector) {
        const el = document.querySelector(selector);
        if (el) {
            console.log("Found target: " + selector);
            el.click();
            return true;
        }
        return false;
    }

    // Interval to check elements frequently
    const loop = setInterval(() => {

        // 1. Cloudflare Checkbox
        // Usually inside shadow-root or iframe, might be tricky from main context
        // But clicking generic buttons helps
        if (clickWhenAvailable("input[type='checkbox']")) return;

        // 2. hCaptcha Checkbox (Inside Iframe usually, but sometimes exposed)
        // Note: Playwright handles frame logic better, this is fallback
        const frames = document.getElementsByTagName("iframe");
        for (let frame of frames) {
            try {
                const checkbox = frame.contentWindow.document.querySelector("#checkbox");
                if (checkbox) {
                    checkbox.click();
                    console.log("✅ Clicked hCaptcha Checkbox!");
                }
            } catch (e) {
                // Cross-origin error is normal
            }
        }

        // 3. 'Verify' Button (OwO specific)
        const verifyBtn = Array.from(document.querySelectorAll("button")).find(b => b.textContent.includes("Verify"));
        if (verifyBtn) verifyBtn.click();

    }, 1000);

    // Stop after 2 minutes to save resources
    setTimeout(() => clearInterval(loop), 120000);

})();
