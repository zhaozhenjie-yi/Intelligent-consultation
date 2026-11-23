const uid = new URL(location.href).searchParams.get('uid');

export const id = uid === null ? '9999' : uid;
