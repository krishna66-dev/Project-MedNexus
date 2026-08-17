<script lang="ts">
	import { onMount } from 'svelte';
	import "../styles/InfiniteBrandCarousel.scss";

	interface Brand {
		name: string;
		logo: string;
	}

	export let brands: Brand[];
	export const speed: number = 1;

	onMount(() => {
		const container = document.querySelector(".logos");
		const slide = document.querySelector(".logos-slide");
		if (slide && container) {
			const copy = slide.cloneNode(true);
			container.appendChild(copy);
		}
	});
</script>

<div class="logos">
	<div class="logos-slide">
		{#each brands as brand, index (index)}
			<img src={brand.logo} alt={brand.name} />
		{/each}
	</div>
	<div class="logos-slide">
		{#each brands as brand, index (index)}
			<img src={brand.logo} alt={brand.name} />
		{/each}
	</div>
	<div class="logos-slide">
		{#each brands as brand, index (index)}
			<img src={brand.logo} alt={brand.name} />
		{/each}
	</div>
</div>
