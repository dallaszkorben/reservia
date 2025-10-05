// ===== CRYPTO UTILITIES =====
// Client-side password hashing utilities

/**
 * Hashes a password using SHA-256 on the client side
 * @param {string} password - The plain text password
 * @returns {Promise<string>} - The hashed password as hex string
 */
async function hashPassword(password) {
    // Convert password string to bytes
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    
    // Hash the password using SHA-256
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    
    // Convert hash to hex string
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    return hashHex;
}