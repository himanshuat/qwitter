/**
 * Retrieve a cookie value by name from document.cookie.
 * Commonly used for extracting the CSRF token ('csrftoken').
 *
 * @param {string} name - Name of the cookie.
 * @returns {string|null} URI-decoded value of the cookie, or null if not found.
 */
export function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
