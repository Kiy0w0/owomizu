/*
This file is part of owo-dusk.

Copyright (c) 2024-present EchoQuill

Portions of this file are based on code by EchoQuill, licensed under the
GNU General Public License v3.0 (GPL-3.0).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
*/

// Simple welcome page script
document.addEventListener("DOMContentLoaded", () => {
    console.log("Mizu Network - Welcome page loaded successfully!");
    
    // Add subtle animation to the welcome brand text
    const brandElement = document.querySelector('.welcome-brand');
    if (brandElement) {
        brandElement.style.transform = 'translateY(20px)';
        brandElement.style.opacity = '0';
        
        setTimeout(() => {
            brandElement.style.transition = 'all 1.5s ease-out';
            brandElement.style.transform = 'translateY(0)';
            brandElement.style.opacity = '1';
        }, 500);
    }
    
    // Add subtle animation to the subtitle
    const subtitleElement = document.querySelector('.welcome-subtitle');
    if (subtitleElement) {
        subtitleElement.style.transform = 'translateY(30px)';
        subtitleElement.style.opacity = '0';
        
        setTimeout(() => {
            subtitleElement.style.transition = 'all 1.5s ease-out';
            subtitleElement.style.transform = 'translateY(0)';
            subtitleElement.style.opacity = '0.8';
        }, 1000);
    }
    
    // Optional: Add click interaction to the brand text
    if (brandElement) {
        brandElement.addEventListener('click', () => {
            brandElement.style.animation = 'glow 0.5s ease-in-out';
            setTimeout(() => {
                brandElement.style.animation = 'glow 3s ease-in-out infinite alternate';
            }, 500);
        });
    }
});

// Optional: Add some interactive effects
document.addEventListener('mousemove', (e) => {
    const container = document.querySelector('.welcome-container');
    if (container) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        // Subtle parallax effect
        container.style.backgroundPosition = `${x * 20}px ${y * 20}px`;
    }
});