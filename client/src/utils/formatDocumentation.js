export const formatDocumentation = (text) => {
    if (!text) return '';

    let formatted = text;

    // Bold text between \*\* \*\*
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Bullet points (lines starting with - or •)
    formatted = formatted.replace(/^[-•]\s+(.*)$/gm, '<li class="ml-4 mb-1 text-gray-400 list-disc">$1</li>');

    // Wrap lists in <ul> tags (simple implementation)
    // Identify blocks of <li>s and wrap them? 
    // For simplicity, just replacing newlines with <br /> for non-list items might be easier for now, 
    // but let's try to group list items.
    // Actually, let's keep it simple: replace newlines with <br /> EXCEPT for list items which block display.
    // Or better: wrapping sections.

    // Section Headers (e.g. "Overview:", "Components:")
    const sections = ['Overview:', 'Components:', 'Architecture Pattern:', 'Data Flow:', 'Security Analysis:'];
    sections.forEach(section => {
        const regex = new RegExp(`^${section}`, 'gm');
        formatted = formatted.replace(regex, `<h3 class="text-blue-400 font-bold text-lg mt-6 mb-3 border-b border-gray-700 pb-2">${section}</h3>`);
    });

    // Paragraphs: double newlines
    formatted = formatted.replace(/\n\n/g, '<div class="mb-4"></div>');

    // Single newlines that are NOT list items or headers
    // formatted = formatted.replace(/\n(?![<])/g, '<br />');

    return formatted;
};
