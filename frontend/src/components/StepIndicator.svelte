<script lang="ts">
  interface Props {
    step: number
    maxReached: number
    onstepclick: (n: number) => void
  }

  const { step, maxReached, onstepclick }: Props = $props()

  const steps = [
    { label: 'LLM Config', n: 1 },
    { label: 'Maps URL', n: 2 },
    { label: 'Compare', n: 3 },
    { label: 'Analysis', n: 4 },
  ]
</script>

<ul class="steps w-full mb-8">
  {#each steps as s}
  <li
    class="step"
    class:step-primary={step >= s.n}
    class:cursor-pointer={maxReached >= s.n}
    onclick={() => onstepclick(s.n)}
  >{s.label}</li>
  {/each}
</ul>
