<script lang="ts">
	import type { LayoutData } from './$types';
	export const data: LayoutData = undefined as any;
	export const params: Record<string, string> = {};
</script>
<svelte:head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
	<link rel="icon" type="image/png" href="/images/mednexus-logo.png" />
	<title>MedNexus</title>
</svelte:head>
<slot />
<style is:global>
	@font-face{font-family:'SF Pro Display';src:url('/fonts/SFPRODISPLAYREGULAR.OTF');font-weight:400}
	@font-face{font-family:'SF Pro Display';src:url('/fonts/SFPRODISPLAYSEMIBOLDITALIC.OTF');font-weight:600}
	@font-face{font-family:'SF Pro Display';src:url('/fonts/SFPRODISPLAYBOLD.OTF');font-weight:700}
	html{font-family:'SF Pro Display',Arial,sans-serif;background:#eef3f4}
</style>
