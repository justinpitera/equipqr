export function formatNumber(input: number): string {
	let output = input.toString();
	if (input > 999) output = `${(input / 1000).toFixed(1)}k`;
	return output;
}
