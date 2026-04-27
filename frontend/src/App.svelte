<script lang="ts">
    import {onMount} from 'svelte'
    import {getConfig} from './lib/api'
    import type {Country} from './lib/api.ts'
    import StepIndicator from './components/StepIndicator.svelte'
    import Step1Config from './components/Step1Config.svelte'
    import Step2Url from './components/Step2Url.svelte'
    import Step3Countries from './components/Step3Countries.svelte'
    import Step4Analysis from './components/Step4Analysis.svelte'

    type stepsType = 1 | 2 | 3 | 4;

    let step: stepsType = $state(1)
    let maxReached: stepsType = $state(1)
    let availableCountries: Country[] = $state([])
    let detectedCountry: Country | null = $state(null)
    let panoramaAvailable = $state(false)
    let selectedCountries: string[] = $state([])
    let streamUrl = $state('')
    let chatContext = $state('')

    onMount(async () => {
        try {
            const cfg = await getConfig()
            if (cfg.configured) {
                step = 2
                maxReached = 2
            }
        } catch (_) {
        }
    })

    function goToStep(n: stepsType) {
        step = n
        if (n > maxReached) maxReached = n
    }

    function onSaved() {
        goToStep(2)
    }

    function onUrlProcessed(data: {
        detectedCountry: Country
        availableCountries: Country[]
        panoramaAvailable: boolean
    }) {
        availableCountries = data.availableCountries
        detectedCountry = data.detectedCountry
        panoramaAvailable = data.panoramaAvailable
        selectedCountries = data.detectedCountry.id ? [data.detectedCountry.id] : []
        goToStep(3)
    }

    function toggleCountry(id: string) {
        const idx = selectedCountries.indexOf(id)
        if (idx >= 0) {
            selectedCountries = selectedCountries.filter((c) => c !== id)
        } else if (selectedCountries.length < 4) {
            selectedCountries = [...selectedCountries, id]
        }
    }

    function onCompared(data: { streamUrl: string; context: string }) {
        streamUrl = data.streamUrl
        chatContext = data.context
        goToStep(4)
    }

    function onStepClick(n: number) {
        if (n <= maxReached) step = n as stepsType
    }
</script>

<nav class="navbar bg-base-200 shadow-sm">
    <div class="navbar-start">
        <a href="/" class="btn btn-ghost text-xl font-bold">Guess Explainr</a>
    </div>
</nav>

<main class="container mx-auto px-4 py-8">
    <StepIndicator {step} {maxReached} {onStepClick}/>

    {#if step === 1}
        <section>
            <div class="card bg-base-200 max-w-lg mx-auto">
                <div class="card-body">
                    <h2 class="card-title">Configure LLM</h2>
                    <Step1Config {onSaved}/>
                </div>
            </div>
        </section>
    {/if}

    {#if step === 2}
        <section>
            <div class="card bg-base-200 max-w-lg mx-auto">
                <div class="card-body">
                    <h2 class="card-title">Paste a Google Maps URL</h2>
                    <Step2Url {onUrlProcessed}/>
                </div>
            </div>
        </section>
    {/if}

    {#if step === 3}
        <section>
            <div class="card bg-base-200 max-w-2xl mx-auto">
                <div class="card-body">
                    <h2 class="card-title">Compare Countries</h2>
                    <Step3Countries
                            {availableCountries}
                            {detectedCountry}
                            {panoramaAvailable}
                            {selectedCountries}
                            togglecountry={toggleCountry}
                            {onCompared}
                    />
                </div>
            </div>
        </section>
    {/if}

    {#if step === 4}
        <section>
            <div class="card bg-base-200 max-w-3xl mx-auto">
                <div class="card-body">
                    <h2 class="card-title">Analysis &amp; Chat</h2>
                    <Step4Analysis {streamUrl} context={chatContext}/>
                </div>
            </div>
        </section>
    {/if}
</main>
