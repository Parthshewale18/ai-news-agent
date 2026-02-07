# How to Contribute

Thank you for your interest in contributing to AI News Agent! 🎉

## Ways to Contribute

1. **Add News Sources**: Suggest trusted AI news sources
2. **Fix Bugs**: Report and fix issues
3. **Improve Documentation**: Help others understand the project
4. **Enhance Filtering**: Improve AI relevance detection
5. **Better Summaries**: Refine summarization prompts
6. **New Features**: Propose and implement features

## Getting Started

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Create a Pull Request

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
official_sources:
  your_source:
    name: "Source Name"
    url: "https://example.com"
    rss: "https://example.com/rss.xml"
    credibility: 90  # 0-100
```

Requirements:
- Must be a trusted source
- Must have RSS feed
- Should focus on AI news

## Code Style

- Use Black for formatting: `black .`
- Follow PEP 8
- Add docstrings to functions
- Write type hints where possible

## Testing

```bash
# Run tests
pytest

# Test specific module
python -m src.ingestion.rss_fetcher
python -m src.filtering.ai_classifier
```

## Pull Request Guidelines

- Clear description of changes
- Link related issues
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass

## Code of Conduct

- Be respectful
- Be inclusive
- Be helpful
- Give constructive feedback

## Questions?

Open an issue or discussion on GitHub!

Thank you for contributing! 🚀
