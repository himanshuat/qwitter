export function initProfileActions() {
	document.querySelectorAll("button.connect").forEach(btn => {
		btn.addEventListener("click", (e) => {
			connect(e.target.dataset.username)
		})
	})
}

function connect(username) {
	fetch(`/profile/${username}/follow/`, { method: 'POST' })
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
