export function initTheme() {
	const themeToggler = document.getElementById("theme-toggler");

	if (!localStorage.getItem("theme")) {
		localStorage.setItem("theme", "auto");
	}

	applyTheme(localStorage.getItem("theme"));

	if (themeToggler) {
		themeToggler.value = localStorage.getItem("theme");
		themeToggler.addEventListener("change", () => {
			localStorage.setItem("theme", themeToggler.value);
			applyTheme(themeToggler.value);
		});
	}

	window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
		if (localStorage.getItem("theme") === "auto") applyTheme("auto");
	});
}

function applyTheme(theme) {
	let finalTheme = theme;
	if (theme === "auto") {
		finalTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
	}
	document.body.dataset.bsTheme = finalTheme;
}
