<div class="skeleton">
    <div class="header"></div>
    <div class="content"></div>
</div>

<style>
    .skeleton {
        width: 100%;
        height: 100%;
        background: #f0f0f0;
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        box-sizing: border-box;
    }

    .header {
        height: 20px;
        width: 60%;
        background: #ddd;
        border-radius: 4px;
        animation: pulse 1.5s infinite;
    }

    .content {
        flex: 1;
        background: #ddd;
        border-radius: 4px;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
</style>
