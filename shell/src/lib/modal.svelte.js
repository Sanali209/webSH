export const modalStore = $state({
    active: null, // { component, props, title }
});

export const openModal = (component, props = {}, title = "Modal") => {
    modalStore.active = { component, props, title };
};

export const closeModal = () => {
    modalStore.active = null;
};
