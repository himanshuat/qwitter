export function initProfileActions() {
	document.querySelectorAll("button.connect").forEach(btn => {
		btn.addEventListener("click", (e) => {
			connect(e.target.dataset.username)
		})
	})
}

function connect(username) {
	fetch(`/profile/${username}/follow/`, {
		method: 'POST',
		headers: {
			'X-CSRFToken': getCookie('csrftoken')
		}
	})
		.then(res => res.json())
		.then(res => {
			if (res.status === "401") {
				window.location.href = window.location.origin + "/login"
			}
			else if (res.status === "404") {
				alert(res.response)
			}
			else {
				location.reload()
			}
		})
}

function getCookie(name) {
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
