export function initToasts() {
	const toastElements = document.querySelectorAll('.toast');
	toastElements.forEach(toastElement => {
		const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
		setTimeout(() => toast.show(), 200);
	});
}
