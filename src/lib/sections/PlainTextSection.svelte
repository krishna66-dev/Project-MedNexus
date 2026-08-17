<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { SectionLayout, ArrowButton } from '$lib';

	const textList = [
		`<p>Meet <span class="bigRed">inCall</span></p>`,
		`<p>An AI-powered assistant that<br/><span class="regularRed">answers patient</span> calls instantly.</p>`,
		`<p>How it works<span class="regularRed">?</span></p>`,
		`<p>Think of it like a <span class="regularBold">car.</span></p>`,
		`<p>The <span class="regularBold">engine</span> uses AI to answer and<br/>book calls.</p>`,
		`<p>The <span class="regularBold">dashboard</span> tracks and<br/>monitors calls in real-time.</p>`,
		`<p>The <span class="regularBold">driver</span> manages two types of<br/>calls.</p>`,
		`<p>Auto calls that are fully automated, no staff<br/>action needed.</p>`,
		`<p>Assist calls that are live and monitored to<br/>action via the traffic lights.</p>`,
		`<p>The <span class="regularBold">traffic lights.</span></p>`,
		`<p><span class="regularBold">Amber (Awaiting)</span><br/>Action suggested by AI for staff to review.</p>`,
		`<p><span class="regularBold">Green (Auto)</span><br/>Action approved and AI proceeds.</p>`,
		`<p><span class="regularBold">Red (Assist)</span><br/>Staff take over.</p>`,
		`<p>Its the <span class="bigRed">future.</span></p>`,
		`<p><span class="regularBold">Less</span> waiting.</p>`,
		`<p><span class="regularBold">Less</span> admin.</p>`,
		`<p><span class="regularRed">More</span> care.</p>`,
	];

	let currentIndex = 0;
	let textContainer: HTMLElement;
	let interval: NodeJS.Timeout;
	let isTransitioning = false;
	let currentSection = 1;
	let autoScrollComplete = false;
	let unsubscribe: (() => void) | null = null;

	const moveToNext = () => {
		if (!textContainer || isTransitioning) return;

		// Stop if we've reached the last item
		if (currentIndex >= textList.length - 1) {
			stopAutoScroll();
			autoScrollComplete = true;
			console.log("Auto-scroll has completed")
			return;
		}
		
		isTransitioning = true;
		const nextIndex = (currentIndex + 1);
		const viewportHeight = window.innerHeight;
		const targetY = -nextIndex * viewportHeight;
		
		// Simple CSS transition approach
		textContainer.style.transform = `translateY(${targetY}px)`;
		
		setTimeout(() => {
			currentIndex = nextIndex;
			isTransitioning = false;
		}, 800); // Match the CSS transition duration
	};

	const startAutoScroll = () => {
		// Only start if we're in section 2 (plain text section)
		if (currentSection !== 2) return;
		
		if (interval) clearInterval(interval);
		
		console.log('Starting auto scroll in section', currentSection);
		interval = setInterval(() => {
			// Double-check we're still in section 2
			if (currentSection === 2) {
				moveToNext();
			}
		}, 2500); // 2.5 seconds between transitions
	};

	const stopAutoScroll = () => {
		console.log('Stopping auto scroll');
		if (interval) {
			clearInterval(interval);
		}
	};

	const handleSectionChange = (section: number) => {
		console.log('Section changed to:', section);
		currentSection = section;
		
		if (section === 2) {
			// We're in the plain text section, start auto scroll
			startAutoScroll();
			if (autoScrollComplete) {
				resetAutoScroll();
			}
		} else {
			// We're not in the plain text section, stop auto scroll
			stopAutoScroll();
		}
	};

	const handleSkip = () => {
		stopAutoScroll();
		moveToNext();
		
		// Restart after skip if still in section 2
		setTimeout(() => {
			if (currentSection === 2) {
				if (autoScrollComplete) {
					resetAutoScroll();
				}
				startAutoScroll();
			}
		}, 1000);
	};

	const resetAutoScroll = () => {
		console.log("Resetting auto-scroller for PlainTextSection")
		autoScrollComplete = false;
		currentIndex = 0;
		textContainer.style.transform = 'translateY(0vh)';
	};

	onMount(() => {
		if (!textContainer) {
			console.error('Text container not found!');
			return;
		}
		
		console.log('PlainTextSection mounted');
		
		// Set initial position and transition
		textContainer.style.transform = 'translateY(0vh)';
		textContainer.style.transition = 'transform 0.8s cubic-bezier(0.4, 0.0, 0.2, 1)';
		
		// Subscribe to section changes via global system
		// Wait a bit for the timeline system to be ready
		setTimeout(() => {
			if ((window as any).sectionChangeSystem) {
				unsubscribe = (window as any).sectionChangeSystem.onSectionChange(handleSectionChange);
				console.log('Subscribed to section changes');
			} else {
				console.warn('Section change system not available, falling back to auto start');
				// Fallback: assume we're in section 2 and start
				setTimeout(() => {
					startAutoScroll();
				}, 1500);
			}
		}, 500);
	});

	onDestroy(() => {
		console.log('PlainTextSection destroyed');
		stopAutoScroll();
		
		// Unsubscribe from section changes
		if (unsubscribe) {
			unsubscribe();
		}
	});
</script>

<SectionLayout className="PlainTextSectionWrapper">
	<div class="PlainTextSectionFixed" id="PlainTextSectionFixed">
		<div class="PlainTextSection" bind:this={textContainer}>
			{#each textList as textItem, index (index)}
				<div class="PlainTextSection__inner" data-index={index}>
					<div class="PlainTextSection__inner__SVH">
						{@html textItem}
					</div>
				</div>
			{/each}
		</div>

		<span class="skipBtn">
			<ArrowButton label="Skip" on:click={handleSkip} />
		</span>
	</div>
</SectionLayout>

<style lang="scss">
	.PlainTextSectionFixed {
		height: 100vh;
		height: 100svh;
		overflow: hidden;
		width: 100%;
		position: relative;
		
		/* Isolate from main scroll system */
		pointer-events: none;

		.skipBtn {
			position: absolute;
			bottom: 1rem;
			right: 2rem;
			z-index: 10;
			pointer-events: auto;
		}
	}

	/* PlainTextSection font */
	@font-face {
		font-family: "SF Pro Display Import";
		src: url("/src/lib/assets/sf-pro-display/SFPRODISPLAYREGULAR.OTF") format("opentype");
	}
	:global(.PlainTextSection__inner__SVH p) {
		font-family: 'SF Pro Display Import';
		font-size: 3rem;
	}
	
	@media (max-width: 768px) {
		:global(.PlainTextSection__inner__SVH p) {
		font-family: 'SF Pro Display Import';
		font-size: 1.7rem;
		}
	}
	
	.PlainTextSection {
		background-color: #ffffff;
		width: 100%;
		opacity: 1;
		color: #000;
		will-change: transform;
		pointer-events: auto;

		&__inner {
			width: 100%;
			height: 100vh;
			height: 100svh;
			font-size: clamp(1.5rem, 4vw, 4rem);
			line-height: 1.1;
			text-align: center;

			&__SVH {
				width: 100%;
				height: 100vh;
				height: 100svh;
				display: grid;
				place-items: center;
			}

			/* Text styling classes */
			:global(.bigRed) {
				color: #ff0000;
				font-weight: 800;
				font-size: 1.5em;
			}

			:global(.regularRed) {
				color: #ff0000;
				font-weight: 600;
			}

			:global(.regularBold) {
				font-weight: 700;
				color: #000000;
			}

			/* Responsive paragraph styling */
			:global(p) {
				margin: 0;
				padding: 0;
				line-height: 1.1;
			}
		}
	}

	/* Enhanced mobile responsiveness */
	@media (max-width: 768px) {
		.PlainTextSection {
			&__inner {
				font-size: clamp(1.2rem, 5vw, 2.5rem);
				line-height: 1.2;

				:global(.bigRed) {
					font-size: 1.5em;
				}
			}
		}

		.PlainTextSectionFixed .skipBtn {
			bottom: 0.5rem;
			right: 1rem;
		}
	}

	@media (max-width: 480px) {
		.PlainTextSection {
			&__inner {
				font-size: clamp(1rem, 6vw, 2rem);
				line-height: 1.3;

				:global(.bigRed) {
					font-size: 1.5em;
				}
			}
		}
	}

	/* For very large screens */
	@media (min-width: 1400px) {
		.PlainTextSection {
			&__inner {
				font-size: clamp(3rem, 3vw, 5rem);
			}
		}
	}
</style>