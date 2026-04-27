"""Discord slash-command entrypoint for transient practice-pack exports."""

from __future__ import annotations

import io
from typing import Literal

import discord
from discord import app_commands

from app.config import get_settings
from app.core.discord_pack import create_discord_practice_pack
from app.core.musicxml import MAX_IMPORT_BYTES

SourceTypeChoice = Literal[
    "self_created",
    "suno_free",
    "suno_paid",
    "public_domain",
    "licensed",
    "private_research",
]


class UkePackDiscordBot(discord.Client):
    """Minimal Discord client with a single /ukepack slash command."""

    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.none())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        settings = get_settings()
        guild_id = settings.discord_bot_guild_id
        if guild_id is None:
            await self.tree.sync()
            return

        guild = discord.Object(id=guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


bot = UkePackDiscordBot()


@bot.tree.command(name="ukepack", description="Upload MusicXML and get a practice-pack PDF.")
@app_commands.describe(
    score_file="MusicXML / XML / MXL attachment",
    source_type="License footer label for the generated PDF",
    confirm_license="Confirm you have rights to upload and use this score",
    level="Arrangement level (1 beginner, 3 advanced)",
    title="Optional PDF title override",
)
async def ukepack_command(
    interaction: discord.Interaction,
    score_file: discord.Attachment,
    source_type: SourceTypeChoice,
    confirm_license: bool,
    level: app_commands.Range[int, 1, 3] = 1,
    title: str | None = None,
) -> None:
    """Generate a PDF from one uploaded MusicXML attachment."""
    if not confirm_license:
        await interaction.response.send_message(
            "License confirmation is required before export. Re-run /ukepack with confirm_license=true.",
            ephemeral=True,
        )
        return
    if score_file.size > MAX_IMPORT_BYTES:
        await interaction.response.send_message(
            f"File too large. Discord bot imports are limited to {MAX_IMPORT_BYTES // (1024 * 1024)} MB.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True, ephemeral=True)
    try:
        result = create_discord_practice_pack(
            filename=score_file.filename,
            content=await score_file.read(),
            source_type=source_type,
            level=level,
            confirm_license=confirm_license,
            title=title,
        )
    except (RuntimeError, ValueError) as exc:
        await interaction.followup.send(str(exc), ephemeral=True)
        return

    await interaction.followup.send(
        result.summary(),
        file=discord.File(io.BytesIO(result.pdf_bytes), filename=result.filename),
        ephemeral=True,
    )


def main() -> None:
    """Run the Discord bot using environment configuration."""
    settings = get_settings()
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required to run the Discord bot")
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":  # pragma: no cover
    main()
