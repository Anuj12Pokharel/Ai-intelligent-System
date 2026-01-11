#!/usr/bin/env python3
"""
Vidhi-AI Command Line Interface
Provides commands for ingestion, querying, and system management.
"""
import click
import os
from vidhi_ai.src.ingestion.pipeline import IngestionPipeline
from vidhi_ai.src.reasoning.chain import LegalChain

@click.group()
def cli():
    """Vidhi-AI - Nepali Legal Intelligence System"""
    pass

@cli.command()
@click.option('--limit', default=None, type=int, help='Limit number of files to process')
@click.option('--raw-dir', default='data/raw', help='Directory containing raw PDFs')
def ingest(limit, raw_dir):
    """Run the ingestion pipeline to process PDFs and build the index."""
    click.echo(f"Starting ingestion from {raw_dir}...")
    pipeline = IngestionPipeline(raw_data_dir=raw_dir)
    pipeline.run_batch(limit=limit)
    click.echo("✓ Ingestion complete!")

@cli.command()
@click.argument('query')
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
def ask(query, api_key):
    """Ask a legal question."""
    if not api_key:
        click.echo("Error: OPENAI_API_KEY not set. Use --api-key or set env variable.", err=True)
        return
    
    click.echo(f"Question: {query}\n")
    chain = LegalChain(api_key=api_key)
    answer = chain.answer(query)
    click.echo(f"Answer:\n{answer}")

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
def serve(host, port):
    """Start the API server."""
    import uvicorn
    from vidhi_ai.src.api.server import app
    
    click.echo(f"Starting Vidhi-AI API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

@cli.command()
def status():
    """Show system status and statistics."""
    from vidhi_ai.src.retrieval.indexer import LegalIndexer
    
    try:
        indexer = LegalIndexer()
        count = indexer.collection.count()
        click.echo(f"✓ ChromaDB connected")
        click.echo(f"  Indexed sections: {count}")
    except Exception as e:
        click.echo(f"✗ Error connecting to ChromaDB: {e}", err=True)
    
    # Check OpenAI
    if os.getenv('OPENAI_API_KEY'):
        click.echo(f"✓ OpenAI API key configured")
    else:
        click.echo(f"✗ OpenAI API key not set")

@cli.command()
@click.option('--category', default='existing-laws', help='Category to scrape (existing-laws, new-laws, etc.)')
@click.option('--limit', default=None, type=int, help='Maximum number of Acts to scrape')
@click.option('--output-dir', default='data/raw', help='Directory to save downloaded files')
def scrape(category, limit, output_dir):
    """Scrape Acts from lawcommission.gov.np"""
    import asyncio
    from vidhi_ai.src.ingestion.scraper import scrape_existing_laws
    
    click.echo(f"Starting scraper for category: {category}")
    click.echo(f"Output directory: {output_dir}")
    if limit:
        click.echo(f"Limit: {limit} Acts")
    else:
        click.echo("Limit: No limit (downloading all)")
    
    click.echo("\nThis will take 2-3 hours. Press Ctrl+C to stop.\n")
    
    # Run async scraper
    try:
        asyncio.run(scrape_existing_laws(
            output_dir=output_dir,
            limit=limit
        ))
        click.echo(f"\n✓ Scraping complete!")
    except KeyboardInterrupt:
        click.echo(f"\n⚠ Scraping interrupted by user")
    except Exception as e:
        click.echo(f"\n✗ Scraping failed: {e}", err=True)

@cli.command()
@click.argument('pdf_path')
@click.option('--output', '-o', help='Output JSON path')
def parse(pdf_path, output):
    """Parse a single PDF and output structured JSON."""
    from vidhi_ai.src.ingestion.parser import NepaliLegalParser
    import json
    
    parser = NepaliLegalParser(pdf_path)
    act = parser.parse()
    
    output_data = act.model_dump_json(indent=2)
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(output_data)
        click.echo(f"✓ Saved to {output}")
    else:
        click.echo(output_data)

if __name__ == '__main__':
    cli()
