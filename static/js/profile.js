import { getCookie } from "./utils.js";

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
