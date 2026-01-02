import { initTheme } from "./theme.js";
import { initToasts } from "./toasts.js";
import { initPostActions } from "./posts.js";
import { initProfileActions } from "./profile.js";

document.addEventListener("DOMContentLoaded", function () {
	initTheme();
	initToasts();
	initPostActions();
	initProfileActions();
});
