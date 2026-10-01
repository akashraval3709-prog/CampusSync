/**
 * CampusSync ERP - Hardware Device Fingerprinting Engine
 * ========================================================
 * File: static/js/device_fingerprint.js
 * 
 * Provides an immutable, deterministic Hardware Fingerprint for anti-proxy protection:
 * - HTML5 Canvas 2D Subpixel Rendering
 * - WebGL GPU Renderer & Vendor Hardware Identification
 * - Screen Physics (Width, Height, Color Depth, Pixel Ratio)
 * - CPU Concurrency & Hardware Touch Capabilities
 * - Platform & Timezone Profiling
 * 
 * Survives full browser history, cache, cookie, and site data clearing!
 */

(function(window) {
    'use strict';

    /**
     * Fast 64-bit Cyb32/FNV-1a Hash Generator (Works on HTTP & HTTPS, zero dependencies)
     */
    function fastHash64(str) {
        let h1 = 0xdeadbeef ^ 0, h2 = 0x41c64e6d ^ 0;
        for (let i = 0, ch; i < str.length; i++) {
            ch = str.charCodeAt(i);
            h1 = Math.imul(h1 ^ ch, 2654435761);
            h2 = Math.imul(h2 ^ ch, 1597334677);
        }
        h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
        h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
        h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
        h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
        
        const part1 = (h1 >>> 0).toString(16).padStart(8, '0').toUpperCase();
        const part2 = (h2 >>> 0).toString(16).padStart(8, '0').toUpperCase();
        return `${part1}-${part2}`;
    }

    /**
     * 1. HTML5 Canvas 2D GPU Rendering Fingerprint
     */
    function getCanvasProfile() {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 240;
            canvas.height = 60;
            const ctx = canvas.getContext('2d');
            if (!ctx) return 'NO_2D_CTX';

            // Text with different fonts and blending
            ctx.textBaseline = 'top';
            ctx.font = "14px 'Arial', 'Helvetica', sans-serif";
            ctx.textBaseline = 'alphabetic';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);

            ctx.fillStyle = '#069';
            ctx.fillText('CampusSync ERP Security, \ud83d\udd12 2026', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Institutional Anti-Proxy Layer', 4, 35);

            // Canvas winding & shapes
            ctx.beginPath();
            ctx.arc(50, 45, 12, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fill();

            return canvas.toDataURL();
        } catch (e) {
            return 'CANVAS_ERR_' + e.message;
        }
    }

    /**
     * 2. WebGL GPU Chipset & Hardware Profile
     */
    function getWebGLProfile() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) return 'NO_WEBGL';

            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            let vendor = 'GENERIC_VENDOR';
            let renderer = 'GENERIC_RENDERER';

            if (debugInfo) {
                vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) || vendor;
                renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || renderer;
            }

            const maxTexSize = gl.getParameter(gl.MAX_TEXTURE_SIZE) || 0;
            const maxVarying = gl.getParameter(gl.MAX_VARYING_VECTORS) || 0;
            const shadingLang = gl.getParameter(gl.SHADING_LANGUAGE_VERSION) || '';

            return `${vendor}~${renderer}~tex:${maxTexSize}~vary:${maxVarying}~sh:${shadingLang}`;
        } catch (e) {
            return 'WEBGL_ERR_' + e.message;
        }
    }

    /**
     * 3. Physical Screen & Hardware Capabilities
     */
    function getHardwareMetrics() {
        const s = window.screen || {};
        const width = s.width || 0;
        const height = s.height || 0;
        const colorDepth = s.colorDepth || 24;
        const pixelRatio = window.devicePixelRatio || 1;
        const cores = navigator.hardwareConcurrency || 4;
        const touchPoints = navigator.maxTouchPoints || 0;
        const platform = navigator.platform || 'Generic';
        let timezone = 'UTC';
        try {
            timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
        } catch(e) {}

        return `SCR:${width}x${height}@${pixelRatio}|CD:${colorDepth}|CPU:${cores}|TOUCH:${touchPoints}|PLT:${platform}|TZ:${timezone}`;
    }

    /**
     * Cached persistent fingerprint in memory
     */
    let cachedHardwareFingerprint = null;

    /**
     * Computes the deterministic Hardware Device Fingerprint:
     * Combines Canvas + WebGL GPU + Screen + CPU into an immutable signature:
     * HW-[PART1]-[PART2]
     */
    function computeHardwareFingerprint() {
        if (cachedHardwareFingerprint) {
            return cachedHardwareFingerprint;
        }

        let persistentFp = null;
        try {
            persistentFp = localStorage.getItem('cs_hw_fingerprint');
        } catch(e) {}

        const canvasData = getCanvasProfile();
        const webglData = getWebGLProfile();
        const hardwareData = getHardwareMetrics();

        const rawCombinedSignature = `${webglData}##${hardwareData}##${canvasData}`;
        const hash = fastHash64(rawCombinedSignature);
        const computedFp = `HW-${hash}`;

        // If Brave shields randomize canvas on refresh, preserve bound fingerprint
        const isBrave = (navigator.brave && typeof navigator.brave.isBrave === 'function');
        if (isBrave && persistentFp && persistentFp.startsWith('HW-')) {
            cachedHardwareFingerprint = persistentFp;
            return persistentFp;
        }

        cachedHardwareFingerprint = persistentFp || computedFp;
        try {
            localStorage.setItem('cs_hw_fingerprint', cachedHardwareFingerprint);
        } catch(e) {}

        return cachedHardwareFingerprint;
    }

    /**
     * Returns Device Model String (e.g. Android Mobile, Windows PC, iPhone)
     */
    function getDeviceModel() {
        const ua = navigator.userAgent || '';
        let model = 'Mobile Device';

        if (/android/i.test(ua)) {
            const match = ua.match(/Android[^;]+; ([^;]+)\)/);
            if (match && match[1]) {
                model = match[1].trim();
            } else {
                model = 'Android Smartphone';
            }
        } else if (/iphone|ipad|ipod/i.test(ua)) {
            model = 'Apple iOS Device';
        } else if (/windows/i.test(ua)) {
            model = 'Windows PC';
        } else if (/macintosh|mac os x/i.test(ua)) {
            model = 'Macintosh';
        } else if (/linux/i.test(ua)) {
            model = 'Linux Machine';
        }

        return model;
    }

    // Expose globally
    window.CampusSyncDevice = {
        getHardwareFingerprint: computeHardwareFingerprint,
        getDeviceModel: getDeviceModel,
        getRawMetrics: getHardwareMetrics
    };

    // Backward-compatible global bindings
    window.getDeviceFingerprint = computeHardwareFingerprint;
    window.getDeviceModel = getDeviceModel;

})(window);
