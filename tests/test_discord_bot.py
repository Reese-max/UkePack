"""Tests for the Discord slash-command entrypoint."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import discord
import pytest

import app.discord_bot as discord_bot
from app.core.discord_pack import DiscordPackResult
from app.core.musicxml import MAX_IMPORT_BYTES


class DummyResponse:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []
        self.deferred: dict[str, bool] | None = None

    async def send_message(self, content: str, *, ephemeral: bool) -> None:
        self.messages.append({"content": content, "ephemeral": ephemeral})

    async def defer(self, *, thinking: bool, ephemeral: bool) -> None:
        self.deferred = {"thinking": thinking, "ephemeral": ephemeral}


class DummyFollowup:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    async def send(
        self,
        content: str,
        *,
        file: discord.File | None = None,
        ephemeral: bool,
    ) -> None:
        self.messages.append({"content": content, "file": file, "ephemeral": ephemeral})


class DummyInteraction:
    def __init__(self) -> None:
        self.response = DummyResponse()
        self.followup = DummyFollowup()


class DummyAttachment:
    def __init__(self, filename: str, payload: bytes, size: int | None = None) -> None:
        self.filename = filename
        self._payload = payload
        self.size = len(payload) if size is None else size
        self.read_calls = 0

    async def read(self) -> bytes:
        self.read_calls += 1
        return self._payload


async def _invoke_command(
    interaction: DummyInteraction,
    attachment: DummyAttachment,
    source_type: str,
    confirm_license: bool,
    level: int,
    title: str | None,
) -> None:
    callback = cast(Any, discord_bot.ukepack_command.callback)
    await callback(interaction, attachment, source_type, confirm_license, level, title)


@pytest.mark.asyncio
async def test_setup_hook_syncs_global_commands_without_guild(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = discord_bot.UkePackDiscordBot()
    sync_calls: list[discord.Object | None] = []

    async def fake_sync(*, guild: discord.Object | None = None) -> None:
        sync_calls.append(guild)

    monkeypatch.setattr(
        discord_bot,
        "get_settings",
        lambda: SimpleNamespace(discord_bot_guild_id=None),
    )
    monkeypatch.setattr(client.tree, "sync", fake_sync)

    await client.setup_hook()

    assert sync_calls == [None]


@pytest.mark.asyncio
async def test_setup_hook_syncs_to_specific_guild_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = discord_bot.UkePackDiscordBot()
    copied_to: list[discord.Object] = []
    synced_to: list[discord.Object | None] = []

    def fake_copy_global_to(*, guild: discord.Object) -> None:
        copied_to.append(guild)

    async def fake_sync(*, guild: discord.Object | None = None) -> None:
        synced_to.append(guild)

    monkeypatch.setattr(
        discord_bot,
        "get_settings",
        lambda: SimpleNamespace(discord_bot_guild_id=42),
    )
    monkeypatch.setattr(client.tree, "copy_global_to", fake_copy_global_to)
    monkeypatch.setattr(client.tree, "sync", fake_sync)

    await client.setup_hook()

    assert [guild.id for guild in copied_to] == [42]
    assert [guild.id if guild is not None else None for guild in synced_to] == [42]


@pytest.mark.asyncio
async def test_ukepack_command_rejects_missing_license_confirmation() -> None:
    interaction = DummyInteraction()
    attachment = DummyAttachment("song.musicxml", b"<score/>")

    await _invoke_command(
        interaction,
        attachment,
        "public_domain",
        False,
        1,
        None,
    )

    assert interaction.response.messages == [
        {
            "content": (
                "License confirmation is required before export. "
                "Re-run /ukepack with confirm_license=true."
            ),
            "ephemeral": True,
        }
    ]
    assert interaction.response.deferred is None
    assert interaction.followup.messages == []
    assert attachment.read_calls == 0


@pytest.mark.asyncio
async def test_ukepack_command_rejects_oversized_attachment() -> None:
    interaction = DummyInteraction()
    attachment = DummyAttachment(
        "huge.musicxml",
        b"",
        size=MAX_IMPORT_BYTES + 1,
    )

    await _invoke_command(
        interaction,
        attachment,
        "public_domain",
        True,
        1,
        None,
    )

    assert interaction.response.messages == [
        {
            "content": (
                "File too large. Discord bot imports are limited to "
                f"{MAX_IMPORT_BYTES // (1024 * 1024)} MB."
            ),
            "ephemeral": True,
        }
    ]
    assert interaction.response.deferred is None
    assert interaction.followup.messages == []
    assert attachment.read_calls == 0


@pytest.mark.asyncio
async def test_ukepack_command_returns_ephemeral_pdf_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    interaction = DummyInteraction()
    attachment = DummyAttachment("twinkle.musicxml", b"<score/>")
    captured: dict[str, object] = {}

    def fake_create_pack(**kwargs: object) -> DiscordPackResult:
        captured.update(kwargs)
        return DiscordPackResult(
            title="Kid Jam",
            filename="Kid_Jam.pdf",
            level=2,
            recommended_level=1,
            key="G major",
            target_key="C major",
            bpm=96,
            chord_count=4,
            pdf_bytes=b"%PDF-1.4 fake",
        )

    monkeypatch.setattr(discord_bot, "create_discord_practice_pack", fake_create_pack)

    await _invoke_command(
        interaction,
        attachment,
        "public_domain",
        True,
        2,
        "Kid Jam",
    )

    assert interaction.response.deferred == {"thinking": True, "ephemeral": True}
    assert captured == {
        "filename": "twinkle.musicxml",
        "content": b"<score/>",
        "source_type": "public_domain",
        "level": 2,
        "confirm_license": True,
        "title": "Kid Jam",
    }
    assert len(interaction.followup.messages) == 1
    sent = interaction.followup.messages[0]
    assert sent["content"] == (
        "PDF ready — **Kid Jam** | Level 2 (rec 1) | G major -> C major | 96 BPM | 4 chords"
    )
    assert sent["ephemeral"] is True
    sent_file = sent["file"]
    assert isinstance(sent_file, discord.File)
    assert sent_file.filename == "Kid_Jam.pdf"
    sent_file.close()


@pytest.mark.asyncio
async def test_ukepack_command_surfaces_pack_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    interaction = DummyInteraction()
    attachment = DummyAttachment("broken.musicxml", b"<score/>")

    def fail_pack(**_: object) -> DiscordPackResult:
        raise RuntimeError("MusicXML parse failed: malformed score")

    monkeypatch.setattr(discord_bot, "create_discord_practice_pack", fail_pack)

    await _invoke_command(
        interaction,
        attachment,
        "public_domain",
        True,
        1,
        None,
    )

    assert interaction.response.deferred == {"thinking": True, "ephemeral": True}
    assert interaction.followup.messages == [
        {
            "content": "MusicXML parse failed: malformed score",
            "file": None,
            "ephemeral": True,
        }
    ]


def test_main_requires_discord_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        discord_bot,
        "get_settings",
        lambda: SimpleNamespace(discord_bot_token=None),
    )

    with pytest.raises(RuntimeError, match="DISCORD_BOT_TOKEN is required"):
        discord_bot.main()


def test_main_runs_bot_with_configured_token(monkeypatch: pytest.MonkeyPatch) -> None:
    observed_tokens: list[str] = []

    monkeypatch.setattr(
        discord_bot,
        "get_settings",
        lambda: SimpleNamespace(discord_bot_token="discord-token"),
    )
    monkeypatch.setattr(discord_bot.bot, "run", observed_tokens.append)

    discord_bot.main()

    assert observed_tokens == ["discord-token"]
