/**
 * CampusSync ERP - WebAuthn Biometric & Screen Lock Device Guard
 * ==============================================================
 * File: static/js/webauthn_device.js
 * 
 * Provides W3C WebAuthn / Passkeys authentication:
 * - Uses hardware security chip (Android Keystore / Apple Secure Enclave / TPM)
 * - Supports Biometric (Fingerprint / Face Unlock) OR Phone Screen Lock PIN / Pattern
 * - Enforces 1 Physical Device = 1 Student policy via excludeCredentials
 *   (If a phone is already bound to one student, Android OS hardware strictly blocks
 *    any other student from registering on that same phone, across ALL browsers).
 */

(function(window) {
    'use strict';

    // Utility: Convert ArrayBuffer to Base64URL string
    function bufferToBase64URL(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary)
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }

    // Utility: Convert Base64URL string to Uint8Array
    function base64URLToBuffer(base64url) {
        let base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
        while (base64.length % 4) {
            base64 += '=';
        }
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    // Generate random 32-byte cryptographic challenge
    function generateChallenge() {
        const arr = new Uint8Array(32);
        window.crypto.getRandomValues(arr);
        return arr;
    }

    // Detect Device Model / OS
    function getDeviceDescription() {
        const ua = navigator.userAgent || '';
        let dev = 'Mobile Device';
        if (/android/i.test(ua)) {
            dev = 'Android Phone';
            const m = ua.match(/;\s*([A-Za-z0-9\s_-]+)\s*Build/i);
            if (m && m[1] && m[1].length < 30 && !m[1].includes('AppleWebKit')) {
                dev = m[1].trim();
            }
        } else if (/iphone/i.test(ua)) {
            dev = 'Apple iPhone';
        } else if (/ipad/i.test(ua)) {
            dev = 'Apple iPad';
        } else if (/windows/i.test(ua)) {
            dev = 'Windows PC';
        } else if (/macintosh/i.test(ua)) {
            dev = 'Apple Mac';
        }
        return dev;
    }

    // Check if WebAuthn platform authenticator (Fingerprint/Screen Lock) is supported
    async function isPlatformAuthenticatorAvailable() {
        if (!window.isSecureContext) return false;
        if (!window.PublicKeyCredential) return false;
        try {
            return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
        } catch (e) {
            return false;
        }
    }

    /**
     * 1. Register Student Device via Native Biometric / Screen Lock
     * Enforces strict 1 Device = 1 Student policy via excludeCredentials
     */
    async function registerDevice(studentInfo) {
        if (!window.isSecureContext) {
            throw new Error('SECURE_CONTEXT_REQUIRED: Android Chrome requires a secure HTTPS connection (e.g. ngrok) to access device biometrics / screen lock.');
        }

        if (!window.PublicKeyCredential) {
            throw new Error('WebAuthn is not supported by your browser. Please use Google Chrome, Edge, Brave, or Samsung Internet.');
        }

        // Fetch all existing registered passkey IDs across the institution to prevent duplicate phone binding
        let excludeList = [];
        try {
            const allCredsRes = await fetch('/student/webauthn/all-credentials');
            const allCredsData = await allCredsRes.json();
            if (allCredsData.success && Array.isArray(allCredsData.credentials)) {
                excludeList = allCredsData.credentials
                    .filter(cid => cid && !cid.startsWith('HW-') && !cid.startsWith('DEV-') && !cid.startsWith('PIN-'))
                    .map(cid => {
                        try {
                            return {
                                id: base64URLToBuffer(cid),
                                type: 'public-key',
                                transports: ['internal']
                            };
                        } catch (e) {
                            return null;
                        }
                    })
                    .filter(Boolean);
            }
        } catch (e) {
            console.warn('Could not fetch excludeCredentials list:', e);
        }

        const challenge = generateChallenge();
        const userId = new TextEncoder().encode(String(studentInfo.student_id || studentInfo.id || 'student'));

        const createOptions = {
            publicKey: {
                rp: {
                    name: 'CampusSync Attendance Security',
                    id: window.location.hostname
                },
                user: {
                    id: userId,
                    name: studentInfo.email || 'student@campussync.local',
                    displayName: studentInfo.full_name || 'CampusSync Student'
                },
                challenge: challenge,
                pubKeyCredParams: [
                    { type: 'public-key', alg: -7 },  // ES256
                    { type: 'public-key', alg: -257 } // RS256
                ],
                authenticatorSelection: {
                    authenticatorAttachment: 'platform', // Native Phone Biometrics / Screen Lock
                    userVerification: 'required',        // Enforce Fingerprint OR Phone Screen Lock PIN/Pattern!
                    requireResidentKey: false
                },
                excludeCredentials: excludeList,         // PREVENTS MULTI-ACCOUNT REGISTRATION ON SAME PHONE!
                timeout: 60000,
                attestation: 'none'
            }
        };

        console.log('[WebAuthn] Prompting Native Biometric / Screen Lock registration...', {
            excludedCount: excludeList.length
        });

        let credential;
        try {
            credential = await navigator.credentials.create(createOptions);
        } catch (err) {
            if (err.name === 'InvalidStateError') {
                throw new Error('DEVICE_ALREADY_REGISTERED: This physical phone is already registered to another student. Institutional policy strictly permits only 1 student per physical device.');
            }
            if (err.name === 'NotAllowedError') {
                throw new Error('Screen lock / Biometric verification was cancelled. Screen lock verification is required to bind your device.');
            }
            throw err;
        }

        if (!credential) {
            throw new Error('Device registration cancelled or failed.');
        }

        const credentialId = bufferToBase64URL(credential.rawId);
        const deviceName = getDeviceDescription();

        // Submit registration to backend
        const res = await fetch('/student/webauthn/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                credential_id: credentialId,
                device_name: deviceName
            })
        });

        const data = await res.json();
        if (!data.success) {
            throw new Error(data.message || 'Failed to save device passkey on server.');
        }

        return {
            credentialId: credentialId,
            deviceModel: deviceName,
            message: data.message
        };
    }

    /**
     * 2. Verify Biometric / Phone Screen Lock
     */
    async function verifyDevice(credentialId) {
        if (!window.isSecureContext) {
            throw new Error('Biometric sensor requires HTTPS. Please access via the secure ngrok domain.');
        }

        const challenge = generateChallenge();
        const allowCredBuffer = base64URLToBuffer(credentialId);

        const getOptions = {
            publicKey: {
                challenge: challenge,
                rpId: window.location.hostname,
                allowCredentials: [{
                    type: 'public-key',
                    id: allowCredBuffer,
                    transports: ['internal']
                }],
                userVerification: 'required', // Enforces Fingerprint OR Screen Lock PIN!
                timeout: 60000
            }
        };

        console.log('[WebAuthn] Requesting assertion for credential:', credentialId);
        let assertion;
        try {
            assertion = await navigator.credentials.get(getOptions);
        } catch (err) {
            if (err.name === 'NotAllowedError') {
                throw new Error('Screen lock / Biometric verification was cancelled. Screen lock authentication is required to mark attendance.');
            }
            throw err;
        }

        if (!assertion) {
            throw new Error('Biometric verification cancelled.');
        }

        const verifiedCredId = bufferToBase64URL(assertion.rawId);
        const deviceName = getDeviceDescription();

        return {
            credentialId: verifiedCredId,
            deviceModel: deviceName
        };
    }

    /**
     * 3. verifyOrRegister: Handles full flow automatically
     */
    async function verifyOrRegister(onStatusUpdate) {
        if (onStatusUpdate) onStatusUpdate('Checking device security status...');

        const statusRes = await fetch('/student/webauthn/status');
        const statusData = await statusRes.json();

        if (!statusData.success) {
            throw new Error('Failed to check device registration status. Please log in again.');
        }

        if (!statusData.has_passkey) {
            if (onStatusUpdate) onStatusUpdate('Unlock with Fingerprint or Screen Lock to bind device...');
            return await registerDevice(statusData);
        } else {
            if (onStatusUpdate) onStatusUpdate('Touch Fingerprint or Enter Screen Lock...');
            try {
                return await verifyDevice(statusData.credential_id);
            } catch (vErr) {
                // If the stored passkey fails on this phone because user switched phones and reset is allowed
                if (statusData.reset_allowed) {
                    if (onStatusUpdate) onStatusUpdate('Device reset active: Registering this phone...');
                    return await registerDevice(statusData);
                }
                throw vErr;
            }
        }
    }

    // Expose globally
    window.CampusSyncWebAuthn = {
        isSupported: isPlatformAuthenticatorAvailable,
        isSecureContext: () => window.isSecureContext,
        registerDevice: registerDevice,
        verifyDevice: verifyDevice,
        verifyOrRegister: verifyOrRegister,
        getDeviceDescription: getDeviceDescription
    };

})(window);
