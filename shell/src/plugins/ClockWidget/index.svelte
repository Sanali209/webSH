<script>
    let time = $state(new Date().toLocaleTimeString());

    $effect(() => {
        const interval = setInterval(() => {
            time = new Date().toLocaleTimeString();
        }, 1000);
        return () => clearInterval(interval);
    });
</script>

<div class="clock-widget">
    <h3>Time</h3>
    <div class="time">{time}</div>
</div>

<style>
    .clock-widget {
        height: 100%;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        padding: 1rem;
        box-sizing: border-box;
    }

    h3 {
        margin: 0 0 0.5rem 0;
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .time {
        font-size: 1.5rem;
        font-weight: bold;
        font-variant-numeric: tabular-nums;
    }
</style>
