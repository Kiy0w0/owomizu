


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

    
    const loop = setInterval(() => {

        
        
        
        if (clickWhenAvailable("input[type='checkbox']")) return;

        
        
        const frames = document.getElementsByTagName("iframe");
        for (let frame of frames) {
            try {
                const checkbox = frame.contentWindow.document.querySelector("#checkbox");
                if (checkbox) {
                    checkbox.click();
                    console.log("✅ Clicked hCaptcha Checkbox!");
                }
            } catch (e) {
                
            }
        }

        
        const verifyBtn = Array.from(document.querySelectorAll("button")).find(b => b.textContent.includes("Verify"));
        if (verifyBtn) verifyBtn.click();

    }, 1000);

    
    setTimeout(() => clearInterval(loop), 120000);

})();
