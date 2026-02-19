export const downloadSVG = () => {
    const svg = document.querySelector('.diagram-viewer svg');
    if (svg) {
        const svgData = new XMLSerializer().serializeToString(svg);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'architecture-diagram.svg';
        link.click();
        URL.revokeObjectURL(url);
    }
};
