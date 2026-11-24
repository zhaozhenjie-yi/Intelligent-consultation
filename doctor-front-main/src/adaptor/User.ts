export function resolveUid(href: string): string | null {
	const url = new URL(href);
	const hashQuery = url.hash.includes('?') ? url.hash.slice(url.hash.indexOf('?') + 1) : '';
	return new URLSearchParams(hashQuery).get('uid') || url.searchParams.get('uid');
}

export function getUserId(): string {
	const uid = resolveUid(location.href);
	if (uid) return uid;
	let anonymous = sessionStorage.getItem('doctorx.anonymousUid');
	if (!anonymous) {
		anonymous = `guest_${crypto.randomUUID().replace(/-/g, '')}`;
		sessionStorage.setItem('doctorx.anonymousUid', anonymous);
	}
	return anonymous;
}
