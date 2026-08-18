<script lang="ts">
	import { SectionLayout, FloatingForm, LogoSlider } from '$lib';

	export const brandList = [
		{
			name: 'Microsoft',
			logo: '/images/microsoft.jpg'
		},
		{
			name: 'NHS Data Security and Protection',
			logo: '/images/nhss.png'
		},
		{
			name: 'Cisco',
			logo: '/images/cisco.png'
		},
		{
			name: 'Cyber Essentials',
			logo: '/images/cyber essentials.png'
		},
		{
			name: 'Health Innovation Manchester',
			logo: '/images/health-innovation.png'
		},
		{
			name: 'NHS Confederation',
			logo: '/images/NHS-CONF.png'
		},
		{
			name: 'ICO',
			logo: '/images/ICO.png'
		},
		{
			name: 'Manchester Metroplitan University',
			logo: '/images/machester-metro.svg'
		}
	];
</script>

<SectionLayout className="BottomSectionWrapper">
	<div class="BottomSection">
		<div class="BottomSection__content">
			<div class="BottomSection__title">
				<h1 class="specialH1">Curious?</h1>
				<h1 style="font-family: Patrick Hand SC">Join Us for all things AI</h1>
			</div>

			<div class="BottomSection__form">
				{#if typeof window !== 'undefined'}
					<FloatingForm />
				{/if}
				<p>
					By joining us, you agree to Ladybird's <a href="/files/inCall TnC.pdf" target="_blank"
						>Terms of Use</a
					>
					and <a href="/files/inCall Privacy Policy.pdf" target="_blank">Privacy Policy</a>
				</p>
			</div>
			<p class="successMessage">Thank you for subscribing!</p>
		</div>
		<div class="BottomSection__brands">
			{#if typeof window !== 'undefined'}
				<LogoSlider brands={brandList} />
			{/if}
		</div>
	</div>
</SectionLayout>

<style lang="scss">
	.BottomSection {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: space-between;
		padding: 2rem;
		margin: 0 auto;
		min-height: 100vh;
		gap: 3rem;
		box-sizing: border-box;
		font-family: 'SF Pro Display Import';

		&__content {
			display: flex;
			flex-direction: column;
			align-items: center;
			gap: 2rem;
			width: 100%;
			max-width: 1200px;
			flex: 1;
			justify-content: center;
			margin: 0 auto;
		}

		&__title {
			display: flex;
			flex-direction: column;
			gap: 0.5rem;
			width: 100%;
			color: #000;
			text-align: center;
			position: relative;
			top: -7vh;

			.specialH1 {
				font-family: 'SF Pro Display Import';
				font-size: clamp(3rem, 6vw, 4rem);
				font-weight: 600;
				line-height: 1.1;
				margin: 0;
			}

			h1 {
				font-size: clamp(1.25rem, 4vw, 2.5rem);
				font-weight: 400;
				line-height: 1.2;
				text-align: center;
				margin: 0;
			}
		}

		&__form {
			display: flex;
			flex-direction: column;
			gap: 1rem;
			width: 100%;
			max-width: 500px;
			color: #bdbdbd;
			margin: 0 auto;

			p {
				font-size: clamp(0.75rem, 2vw, 0.9rem);
				color: #666;
				text-align: center;
				line-height: 1.4;
				padding: 0;
				margin: 0.5rem 0 0 0;
			}

			a {
				text-decoration: none;
				color: #000;
				font-weight: 700;

				&:hover {
					text-decoration: underline;
				}
			}

			button {
				width: 100%;
				padding: 1rem;
				border: none;
				background-color: #000;
				color: #fff;
				font-size: clamp(1rem, 3vw, 1.25rem);
				cursor: pointer;
				transition: background-color 0.3s;
				border-radius: 4px;

				&:hover {
					background-color: #ff0000;
				}

				span {
					display: inline-block;
				}

				svg {
					animation: spin 1s ease-in-out infinite;
					display: none;
				}
			}
		}

		&__brands {
			width: 100%;
			overflow: hidden;
			margin-top: auto;
			max-height: 150px;
			display: flex;
			align-items: center;
			justify-content: center;
		}

		.successMessage {
			color: #04db00;
			font-size: clamp(1rem, 3vw, 1.25rem);
			font-weight: 700;
			display: none;
			text-align: center;
		}
	}

	// Tablet styles
	@media (max-width: 1024px) and (min-width: 769px) {
		.BottomSection {
			padding: 2rem 1.5rem;
			gap: 2.5rem;

			&__content {
				gap: 2rem;
			}

			&__title {
				.specialH1 {
					font-size: 3.5rem;
				}

				h1 {
					font-size: 1.5rem;
				}
			}

			&__brands {
				max-height: 130px;
			}
		}
	}

	// Mobile styles
	@media (max-width: 768px) {
		.BottomSection {
			padding: 1.5rem 1rem;
			margin: 0;
			min-height: 100svh;
			gap: 2rem;
			justify-content: center;

			&__content {
				gap: 1.5rem;
				width: 100%;
				padding: 0;
			}

			&__title {
				gap: 0.5rem;
				width: 100%;
				position: relative;
				top: -12vh;

				.specialH1 {
					font-size: clamp(3rem, 8vw, 3.5rem);
					line-height: 1.1;
				}

				h1 {
					font-size: clamp(1.1rem, 5vw, 1.5rem);
					line-height: 1.2;
				}
			}

			&__form {
				width: 100%;
				max-width: 100%;
				gap: 1rem;

				p {
					font-size: clamp(0.7rem, 3vw, 0.8rem);
					padding: 0 0.5rem;
					line-height: 1.3;
				}

				button {
					padding: 0.875rem 1rem;
					font-size: 1rem;
				}
			}

			&__brands {
				margin-top: 1rem;
			}
		}
	}

	// Small mobile styles
	@media (max-width: 480px) {
		.BottomSection {
			padding: 1rem 0.75rem;
			gap: 1.5rem;
			min-height: 100svh;

			&__content {
				gap: 1.25rem;
				width: 100%;
			}

			&__title {
				gap: 0.25rem;

				.specialH1 {
					font-size: clamp(3rem, 9vw, 3.5rem);
					line-height: 1;
				}

				h1 {
					font-size: clamp(1rem, 5vw, 1.25rem);
					line-height: 1.1;
				}
			}

			&__form {
				gap: 0.875rem;

				p {
					font-size: 0.7rem;
					line-height: 1.3;
					padding: 0 0.25rem;
				}

				button {
					padding: 0.8rem;
					font-size: 0.95rem;
				}
			}

			.successMessage {
				font-size: 1rem;
			}
		}
	}

	// Extra small screens
	@media (max-width: 360px) {
		.BottomSection {
			padding: 1rem 0.5rem;

			&__title {
				.specialH1 {
					font-size: 3rem;
				}

				h1 {
					font-size: 0.95rem;
				}
			}

			&__form {
				p {
					font-size: 0.65rem;
				}
			}
		}
	}

	// Large screens
	@media (min-width: 1440px) {
		.BottomSection {
			padding: 3rem 2rem;
			gap: 4rem;

			&__content {
				gap: 3rem;
			}

			&__title {
				.specialH1 {
					font-size: 4.5rem;
				}

				h1 {
					font-size: 3rem;
				}
			}

			&__form {
				button {
					padding: 1.25rem;
					font-size: 1.5rem;
				}

				p {
					font-size: 1rem;
				}
			}

			&__brands {
				max-height: 200px;
			}
		}
	}

	// Animation keyframes
	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
