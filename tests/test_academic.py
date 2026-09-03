from xavierlabs.tools.academic import AcademicDiscoveryTool, AcademicPaper


def test_academic_paper_model():
    paper = AcademicPaper(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        abstract="The dominant sequence transduction models are based on complex recurrent neural networks...",
        year=2017,
        url="https://arxiv.org/abs/1706.03762",
        source="arxiv",
        citations=120000,
    )

    data = paper.to_dict()
    assert data["title"] == "Attention Is All You Need"
    assert data["year"] == 2017
    assert data["source"] == "arxiv"
    summary = paper.format_summary()
    assert "[ARXIV]" in summary
    assert "Vaswani" in summary


def test_discovery_tool_instantiation():
    tool = AcademicDiscoveryTool(timeout=5.0)
    assert tool.timeout == 5.0
