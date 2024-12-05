const maxFiles = 4;

export function triggerFileInput(): void {
	const fileInput = document.getElementById("file-input") as HTMLInputElement;
	if (fileInput) {
		fileInput.click();
	} else {
		console.error("File input element not found.");
	}
}

export function handleFileUpload(event: Event): void {
	const fileList = document.getElementById("file-list") as HTMLUListElement;
	const fileInput = document.getElementById("file-input") as HTMLInputElement;
	if (!fileInput || !fileList) {
		console.error("file-list or file-input is missing in the page!");
		return;
	}
	const target = event.target as HTMLInputElement;
	const files = Array.from(target.files || []);
	if (files.length > maxFiles) {
		alert(`You can only upload up to ${maxFiles} files.`);
		fileInput.value = "";
		return;
	}
	fileList.innerHTML = "";
	files.forEach((file, index) => {
		const listItem = document.createElement("li");
		listItem.textContent = `${index + 1}. ${file.name}`;
		fileList.appendChild(listItem);
	});
}

export function handleFormSubmit(event: Event): void {
	event.preventDefault();
	const fileInput = document.getElementById("file-input") as HTMLInputElement;
	if (!fileInput) {
		console.error("file-input is missing in the page!");
		return;
	}
	const productDetails = (
		document.getElementById("product-details") as HTMLTextAreaElement
	).value;
	const issueDescription = (
		document.getElementById("issue-description") as HTMLTextAreaElement
	).value;
	alert(
		`Form submitted with the following details:\nProduct Details: ${productDetails}\nIssue Description: ${issueDescription}\nNumber of Files: ${(fileInput.files || []).length}`,
	);
}
