<script lang="ts">
	export let className: string;
</script>

<section class={`SectionLayout ${className}`}>
	<div class="SectionLayout__inner">
		<slot />
	</div>
</section>

<style lang="scss">
	.SectionLayout {
		height: 100vh;
		height: 100svh;
		overflow-y: hidden;
		background-color: #ffffff;
		display: flex;

		&__inner {
			width: 100%;
			min-height: 100vh;
			min-height: 100svh;
			max-width: 1440px;
			margin: 0 auto;
			display: flex;
			position: relative;
		}
	}
</style>
