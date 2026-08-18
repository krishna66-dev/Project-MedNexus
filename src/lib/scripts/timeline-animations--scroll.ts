import gsap from "gsap";
import { Observer } from "gsap/Observer";
import { switchTab } from "../utils/helpers";

gsap.registerPlugin(Observer);

let currSection = 1;
let currTab = 0;
let isAnimating = false;
let isLaptopPlaying = false;

// Event system for section changes
const sectionChangeCallbacks: ((section: number) => void)[] = [];

export const onSectionChange = (callback: (section: number) => void) => {
	sectionChangeCallbacks.push(callback);
	// Immediately call with current section
	callback(currSection);
	
	// Return unsubscribe function
	return () => {
		const index = sectionChangeCallbacks.indexOf(callback);
		if (index > -1) {
			sectionChangeCallbacks.splice(index, 1);
		}
	};
};

// Make section change system available globally without imports
if (typeof window !== 'undefined') {
	(window as any).sectionChangeSystem = {
		onSectionChange: (callback: (section: number) => void) => {
			sectionChangeCallbacks.push(callback);
			// Immediately call with current section
			callback(currSection);
			
			// Return unsubscribe function
			return () => {
				const index = sectionChangeCallbacks.indexOf(callback);
				if (index > -1) {
					sectionChangeCallbacks.splice(index, 1);
				}
			};
		},
		getCurrentSection: () => currSection
	};
}

const notifySectionChange = (section: number) => {
	sectionChangeCallbacks.forEach(callback => callback(section));
};

const resetIsAnimating = () => {
	setTimeout(() => {
		isAnimating = false;
	}, 400);
};

// Query elements - will be set when DOM is ready
let mainWrap: HTMLElement | null = null;
let video = null;
let screen = null;
let skipBtn: HTMLElement | null = null;

// Navigation helpers (no-scrollbar, wheel/touch driven)
// One scroll gesture advances exactly one section.
function goToSection(target: number) {
	if (!mainWrap) return;
	if (isAnimating) return;
	if (target === currSection) return;
	if (target < 1 || target > 3) return;

	const targetY = -((target - 1) / 3) * 100;

	gsap.to(mainWrap, {
		yPercent: targetY,
		ease: "power4.inOut",
		duration: 1,
		onStart: () => (isAnimating = true),
		onComplete: () => {
			currSection = target;
			notifySectionChange(currSection); // Notify about section change
			resetIsAnimating();
		},
	});
}

function goNext() {
	switch (currSection) {
		case 1:
			goToSection(2);
			break;
		case 2:
			goToSection(3);
			break;
		case 3:
			goToSection(4);
			break;
		case 4:
			// stay on last
			break;
	}
}

function goPrev() {
	switch (currSection) {
		case 1:
			// stay on first
			break;
		case 2:
			goToSection(1);
			break;
		case 3:
			goToSection(2);
			break;
		case 4:
			goToSection(3);
			break;
	}
}

// Export current section getter
export const getCurrentSection = () => currSection;

// Initialize immediately when script loads
// Wait for DOM to be ready
if (typeof document !== "undefined") {
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initWhenReady);
	} else {
		initWhenReady();
	}
}

function initWhenReady() {
	// Wait a bit for Svelte to render
	setTimeout(() => {
		// Query elements when DOM is ready
		mainWrap = document.querySelector(".MainWrap__inner") as HTMLElement;
		skipBtn = document.querySelector(".skipBtn") as HTMLElement;

		if (!mainWrap) {
			setTimeout(() => {
				mainWrap = document.querySelector(".MainWrap__inner") as HTMLElement;
				if (mainWrap) {
					initAnimations();
				}
			}, 500);
			return;
		}

		initAnimations();
	}, 300);
}

function initAnimations() {
	if (!mainWrap) return;

	// Skip button: jump directly to Phone section (3) on user click
	if (skipBtn) {
		skipBtn.addEventListener("click", () => {
			goToSection(3);
		});
	}

	// Use GSAP Observer to capture wheel/touch and control sections without scrollbar
	Observer.create({
		target: window,
		type: "wheel,pointer",
		onUp: () => {
			// up = previous
			if (isAnimating) return;
			goPrev();
		},
		onDown: () => {
			// down = next
			if (isAnimating) return;
			goNext();
		},
		tolerance: 10, // small movements ignored
		preventDefault: true, // keep page fixed without a scrollbar
		capture: true,
	});
	// touchscreen devices
	Observer.create({
		target: window,
		type: "touch",
		onUp: () => {
			// up = previous
			if (isAnimating) return;
			goNext();
		},
		onDown: () => {
			// down = next
			if (isAnimating) return;
			goPrev();
		},
		tolerance: 10, // small movements ignored
		preventDefault: true, // keep page fixed without a scrollbar
		capture: true,
	})
	// Notify initial section
	notifySectionChange(currSection);
}

window.onbeforeunload = function () {
	window.scrollTo(0, 0);
};