// ===== CRYPTO UTILITIES =====
// Client-side password hashing utilities for secure authentication
//
// PROBLEM SOLVED: Mobile login failure in non-secure HTTP contexts
// 
// ISSUE: The Web Crypto API (crypto.subtle) requires a secure context (HTTPS) to function.
// When users access the app via HTTP on mobile devices (e.g., http://192.168.1.100:5000),
// the crypto.subtle.digest() method is unavailable, causing "Password hashing failed" errors.
//
// SOLUTION: Implemented a fallback SHA-256 algorithm that works in all contexts (HTTP/HTTPS)
// and produces identical results to the Web Crypto API, ensuring consistent authentication
// across desktop (HTTPS) and mobile (HTTP) environments.
//
// SECURITY: Passwords are hashed client-side before transmission to prevent plain-text
// password exposure over the network. The server stores and compares these SHA-256 hashes.

/**
 * Hashes a password using SHA-256 with automatic fallback for non-secure contexts
 * 
 * CONTEXT HANDLING:
 * - HTTPS (secure context): Uses native Web Crypto API for optimal performance
 * - HTTP (non-secure context): Uses custom SHA-256 implementation for compatibility
 * 
 * Both methods produce identical SHA-256 hashes, ensuring seamless authentication
 * regardless of connection type (mobile HTTP vs desktop HTTPS).
 * 
 * @param {string} password - The plain text password to hash
 * @returns {Promise<string>} - SHA-256 hash as 64-character hex string
 * 
 * @example
 * // Both contexts produce: "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
 * const hash = await hashPassword("admin");
 */
async function hashPassword(password) {
    // PREFERRED: Use Web Crypto API in secure contexts (HTTPS)
    // This is the standard, optimized browser implementation
    if (window.isSecureContext && crypto.subtle) {
        try {
            // Convert password string to UTF-8 bytes
            const encoder = new TextEncoder();
            const data = encoder.encode(password);
            
            // Generate SHA-256 hash using native browser API
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            
            // Convert binary hash to hexadecimal string
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            
            return hashHex;
        } catch (error) {
            console.warn('Web Crypto API failed, falling back to custom implementation:', error);
        }
    }
    
    // FALLBACK: Custom SHA-256 implementation for non-secure contexts (HTTP)
    // This ensures mobile users can login when accessing via IP address over HTTP
    // Produces identical results to Web Crypto API for consistent authentication
    const hash = await simpleHash(password);
    return hash;
}

/**
 * Custom SHA-256 implementation for non-secure HTTP contexts
 * 
 * PURPOSE: Provides SHA-256 hashing when Web Crypto API is unavailable (HTTP contexts)
 * COMPATIBILITY: Produces identical results to crypto.subtle.digest('SHA-256')
 * 
 * TECHNICAL DETAILS:
 * - Implements RFC 6234 SHA-256 specification
 * - Uses proper big-endian bit length encoding (critical for correct results)
 * - Handles UTF-8 string encoding correctly
 * - Produces standard 64-character hexadecimal output
 * 
 * WHY NEEDED: Mobile browsers accessing via HTTP (http://192.168.1.100:5000) 
 * cannot use Web Crypto API, but this fallback ensures identical hash generation.
 * 
 * @param {string} str - String to hash (typically a password)
 * @returns {Promise<string>} - SHA-256 hash as 64-character hex string
 */
async function simpleHash(str) {
    // Convert string to UTF-8 bytes
    const utf8 = unescape(encodeURIComponent(str));
    const bytes = [];
    for (let i = 0; i < utf8.length; i++) {
        bytes.push(utf8.charCodeAt(i));
    }
    
    // SHA-256 implementation
    const K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];
    
    let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
    let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
    
    // Pre-processing
    const msgLen = bytes.length;
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    
    // CRITICAL: Append message length in big-endian format (64-bit)
    // This encoding format is essential for producing correct SHA-256 results
    // that match the Web Crypto API output
    const bitLen = msgLen * 8;
    // High 32 bits (always 0 for reasonable message lengths < 512MB)
    bytes.push(0, 0, 0, 0);
    // Low 32 bits in big-endian byte order (most significant byte first)
    bytes.push((bitLen >>> 24) & 0xff);  // Bits 31-24
    bytes.push((bitLen >>> 16) & 0xff);  // Bits 23-16  
    bytes.push((bitLen >>> 8) & 0xff);   // Bits 15-8
    bytes.push(bitLen & 0xff);           // Bits 7-0
    
    // Process chunks
    for (let chunk = 0; chunk < bytes.length; chunk += 64) {
        const w = new Array(64);
        
        for (let i = 0; i < 16; i++) {
            w[i] = (bytes[chunk + i * 4] << 24) | (bytes[chunk + i * 4 + 1] << 16) |
                   (bytes[chunk + i * 4 + 2] << 8) | bytes[chunk + i * 4 + 3];
        }
        
        for (let i = 16; i < 64; i++) {
            const s0 = rightRotate(w[i - 15], 7) ^ rightRotate(w[i - 15], 18) ^ (w[i - 15] >>> 3);
            const s1 = rightRotate(w[i - 2], 17) ^ rightRotate(w[i - 2], 19) ^ (w[i - 2] >>> 10);
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
        }
        
        let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
        
        for (let i = 0; i < 64; i++) {
            const S1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
            const ch = (e & f) ^ (~e & g);
            const temp1 = (h + S1 + ch + K[i] + w[i]) >>> 0;
            const S0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
            const maj = (a & b) ^ (a & c) ^ (b & c);
            const temp2 = (S0 + maj) >>> 0;
            
            h = g; g = f; f = e; e = (d + temp1) >>> 0;
            d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
        }
        
        h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0; h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0;
        h4 = (h4 + e) >>> 0; h5 = (h5 + f) >>> 0; h6 = (h6 + g) >>> 0; h7 = (h7 + h) >>> 0;
    }
    
    return [h0, h1, h2, h3, h4, h5, h6, h7].map(h => h.toString(16).padStart(8, '0')).join('');
}

/**
 * Performs right rotation of 32-bit integer (required for SHA-256 algorithm)
 * @param {number} value - 32-bit integer to rotate
 * @param {number} amount - Number of positions to rotate right
 * @returns {number} - Right-rotated 32-bit integer
 */
function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount));
}